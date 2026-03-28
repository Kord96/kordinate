---
description: Detected architectural and design patterns for kordinate project
generated: 2026-03-28
project: kordinate
---
# Detected Patterns

## Summary

Kordinate is a multi-agent orchestration platform built primarily in Bash, Node.js, and YAML. It exhibits a clear **plugin architecture** with 7 specialized agents, each with isolated identities, skills, memory, and kord contracts. The system uses a **hook-based chain of responsibility** for permission enforcement (guard.sh) and lifecycle events (agent-memory.sh, worktree-push.sh). The MCP server (beorn) acts as both a **factory** and **mediator**, spawning agents on demand with loaded identities. Strong **RBAC** patterns are present at both the application layer (guard.sh ACLs) and Kubernetes layer (agent-rbac.yaml). The codebase is well-structured with minimal anti-patterns; the main concern is the bash-heavy implementation where shell parsing of complex inputs can be fragile.

## Architectural Patterns

| Pattern | Location | Confidence | Evidence |
|---------|----------|------------|----------|
| Plugin Architecture | `kordinate/agents/*/` (7 agents, each with IDENTITY.md, skills/, memory/, kords/) | High | Each agent is a self-contained plugin with its own identity, skills, memory, and contracts. New agents are discovered dynamically from KORD.json or filesystem scanning (server.js:30-53). |
| Modular Monolith | Project-wide: agents share a single repo, PVC, and config.yaml | High | All agents live in one repo with shared infrastructure (config.yaml, cache.sh, hooks), deployed together on a shared PVC. Clear module boundaries but single deployment unit. |
| Microservices (Partial) | `kordinate/agents/deployer/skills/infra/manifests/master-agent-factory.yaml` | Medium | Agent-factory runs as a separate K8s Deployment with its own Service, health checks, and KEDA scaling. However, agents share state via PVC rather than APIs, so this is microservices at the infrastructure layer only. |
| Hook System / Interceptor | `kordinate/settings.json`, `kordinate/hooks/guard.sh`, `kordinate/hooks/agent-memory.sh`, `kordinate/hooks/worktree-push.sh` | High | PreToolUse and PostToolUse hooks registered in settings.json intercept tool calls. Guard.sh runs before Write/Edit/Bash; agent-memory.sh runs before Agent spawning; worktree-push.sh runs after Bash. Classic interceptor/filter pattern. |
| Configuration Management | `kordinate/profile/config.yaml`, `kordinate/profile/config-acl.yaml`, `kordinate/agents/deployer/skills/infra/topology.yaml` | High | Centralized config.yaml holds all cluster IPs, ports, services. topology.yaml maps manifests to namespaces. ACL file governs field-level ownership. All referenced by deploy scripts, hooks, and agents. |
| Infrastructure as Code | `kordinate/agents/deployer/skills/infra/manifests/` (16 YAML files), `kordinate/agents/deployer/skills/infra/images/` (4 Dockerfiles) | High | Full K8s manifest set (Deployments, Services, RBAC, KEDA ScaledObjects) plus container build contexts. Managed declaratively with kustomize overlays generated from config.yaml. |
| Pipeline / Filter | `kordinate/hooks/agent-memory.sh` | High | Memory regeneration follows a pipeline: shared memory -> instructions -> static knowledge -> kord discovery -> notes. Each stage appends to the output, with conditional inline vs. index based on size thresholds. |

## Design Patterns

| Pattern | Location | Confidence | Evidence |
|---------|----------|------------|----------|
| Factory | `kordinate/lib/mcp-agent-server/server.js` (loadAgentNames, loadSystemPrompt, invokeAgent) | High | Beorn is literally named "agent-factory" in K8s. It dynamically creates agent instances by loading identity + memory, then spawning claude with the assembled system prompt. The `delegate` tool is the factory method. |
| Mediator | `kordinate/lib/mcp-agent-server/server.js` (kord tool, lines 277-327) | High | The `kord` tool routes requests between agents via contracts. It looks up the provider, checks cache, assembles the prompt with guidelines, invokes the provider agent, and caches the result. Agents communicate only through beorn, not directly. |
| Chain of Responsibility | `kordinate/hooks/guard.sh` (guard_write, guard_bash, guard_grafana_mcp) | High | Guard.sh routes based on tool type (Write/Edit -> guard_write, Bash -> guard_bash, mcp__grafana* -> guard_grafana_mcp). Within each handler, multiple rules are checked in sequence with early allow/deny exits. Falls through to `allow` at the end. |
| Strategy | `kordinate/hooks/guard.sh` (check_auth function + per-domain guards) | High | Different authentication strategies per domain: scribe for .kord/ files, deployer for kubectl/git-push, sauron for Grafana. The check_auth function is the strategy interface; the case statements select the strategy. |
| Facade | `installer/kordinate-cli` | High | The CLI exposes simple commands (init, join, connect) that orchestrate complex sequences: k3s installation, kubeconfig setup, workstation deployment, node joining. Hides complexity behind `kordinate init`. |
| Cache-Aside | `kordinate/lib/mcp-agent-server/server.js` (kord tool, lines 300-305), `kordinate/lib/kord-expiry.sh` | High | Kord tool checks cache freshness via expiry.sh before invoking agent. On miss, spawns agent, then writes result to data file + .valid timestamp. Two-stage expiry uses change magnitude + age decay to determine staleness. |
| RBAC | `kordinate/hooks/guard.sh`, `kordinate/profile/config-acl.yaml`, `kordinate/agents/deployer/skills/infra/manifests/agent-rbac.yaml` | High | Three RBAC layers: (1) guard.sh enforces agent authentication via lock files, (2) config-acl.yaml defines field-level ownership of config.yaml paths, (3) K8s ClusterRole/ClusterRoleBinding with readonly and deployer tiers. |
| Decorator | `kordinate/hooks/agent-memory.sh` | Medium | The hook decorates agents before spawning by assembling a MEMORY.md that wraps shared memory + instructions + static knowledge + kord discovery around the agent's own notes. Enhances the agent's context without modifying its identity. |
| Proxy | `kordinate/hooks/guard.sh` (PreToolUse hook) | High | Guard.sh acts as a protection proxy for Write, Edit, Bash, and MCP tools. It intercepts every call, validates permissions, and either allows or denies with a reason. The tool user never interacts with the hook directly. |
| State Machine (Implicit) | `kordinate/lib/kord-expiry.sh` (fresh/stale/uncertain states) | Medium | Kord expiry has three states: fresh (exit 0), stale (exit 1), uncertain (exit 2). Transitions depend on age, change magnitude, and threshold comparison. Not a formal state machine but exhibits state-based behavior. |
| Singleton | `kordinate/profile/config.yaml` | Medium | Single source of truth for all cluster configuration. Referenced by deployer manifests, installer CLI, hooks, and agents. Only one instance exists; all components read from it. Field-level ACL enforces single-writer semantics per section. |
| Command | `kordinate/agents/deployer/skills/infra/SKILL.md`, `kordinate/agents/*/skills/` | Medium | Each skill (infra, config, keys, overlay, preflight, etc.) encapsulates an operation with parameters. Skills are invoked via slash commands (/infra roll, /infra bootstrap). The SKILL.md defines the command interface; execution is deferred to the agent. |
| Builder | `kordinate/hooks/agent-memory.sh` (MEMORY.md assembly) | Medium | The script builds MEMORY.md incrementally: adds shared section, then instructions, then knowledge (inline or index), then kords, then notes. Each section is conditionally included based on existence and size. Progressive construction of a complex document. |
| Dependency Injection | `kordinate/lib/mcp-agent-server/server.js` (environment variables), `kordinate/settings.json` (env block) | Medium | Agent behavior is configured via environment variables (KORDINATE_HOME, REPO_ROOT, PORT, HOME). settings.json injects KORDINATE_HOME into the hook environment. K8s manifests inject all paths via env vars. |
| Idempotent Operations | `kordinate/agents/deployer/skills/infra/SKILL.md` ("All subcommands are idempotent") | Medium | Explicitly documented: all infra subcommands (bootstrap, roll, stop, clean, migrate) are idempotent. The installer CLI's init/join commands also exhibit idempotency (check-before-act patterns). |
| Repository | `KORD.json` | Medium | KORD.json serves as a registry/repository of all managed files, their descriptions, curation status, and preload assignments. Used by guard.sh to determine if a file is curated/templated, and by server.js to discover agents. |
| Secret Management | `kordinate/hooks/guard.sh` (check_auth via lock files), `kordinate/profile/locks/` | Medium | Authentication uses file-based tokens: agent writes to /tmp/.agent-auth, compared against profile/locks/agent. Lock files per agent (deployer, sauron, scribe) gate privileged operations. |
| Structured Logging | `kordinate/lib/mcp-agent-server/server.js` (log function, lines 332-339) | Medium | Beorn uses timestamped structured logging with JSON data payloads: `[beorn HH:MM:SS.mmm] message {json}`. Request logging middleware logs method, path, MCP method, and session ID. |
| GitOps (Partial) | `kordinate/agents/deployer/skills/infra/` (manifests + overlays + topology.yaml) | Medium | Infrastructure is defined declaratively in git (manifests, topology.yaml, config.yaml). Overlays are generated from config. Changes flow through git branches/worktrees. Not fully GitOps (no automated reconciliation loop like ArgoCD). |
| Scale-to-Zero | `kordinate/agents/deployer/skills/infra/manifests/master-agent-factory.yaml` (KEDA ScaledObject) | High | Agent-factory uses KEDA to scale 0-to-1 based on Prometheus HTTP request rate. Cooldown of 300s. Default replicas: 0. Explicit scale-to-zero serverless pattern. |
| Worktree Isolation | `bin/claude-session` | High | Each Claude session runs in an isolated git worktree on a session/* branch. Tmux window index determines the worktree. On exit, empty sessions are cleaned up; dirty ones are auto-committed. Provides workspace isolation without repo cloning. |

## Anti-Patterns

| Anti-Pattern | Location | Severity | Evidence |
|-------------|----------|----------|----------|
| Stringly Typed | `kordinate/hooks/guard.sh` (bash command parsing, lines 140-198) | Medium | Guard.sh parses git push commands via regex/grep to extract branch names and repo roots. Fragile string matching on shell commands (e.g., `*git\ push*`, grep for branch names). Edge cases in quoting or command chaining could bypass guards. |
| Swallowed Exception | `kordinate/lib/mcp-agent-server/server.js` (lines 42, 50, 103) | Low | Multiple `catch { /* fall through */ }` blocks in loadAgentNames and loadSystemPrompt silently discard errors. While intentional (best-effort loading), it makes debugging discovery failures harder. |
| Magic Numbers | `kordinate/lib/mcp-agent-server/server.js` (line 144: 300000ms timeout), `kordinate/lib/kord-expiry.sh` (line 57-58: threshold 0.05, stale 0.30, max_age 7d) | Low | Hardcoded timeout of 300s for agent invocation. Expiry defaults (0.05, 0.30, 7 days) are embedded in Python code rather than named constants. The 300s timeout in server.js is not configurable. |
| Config Sprawl (Minor) | `kordinate/profile/config.yaml`, `kordinate/settings.json`, `kordinate/agents/deployer/skills/infra/topology.yaml`, `KORD.json` | Low | Configuration is spread across 4+ files in different formats (YAML, JSON). Each serves a distinct purpose, so this is mild. However, the relationship between config.yaml, topology.yaml, and generated overlays requires understanding multiple files to reason about deployment. |
| Shell Injection Risk | `kordinate/hooks/guard.sh` (line 51: Python inline with shell variables) | Low | Config ACL check passes shell variables (OLD_STR) into an inline Python script via environment variables. While environment-based passing is safer than interpolation, the pattern of embedding Python in bash with external inputs warrants care. |
| Lava Flow (Minor) | `kordinate/lib/mcp-agent-server/server.js` (lines 365-386: stateless MCP creating new server per request) | Low | Each POST /mcp creates a new McpServer + transport, registers all tools, then discards them. The comment says "stateless: each request gets its own server + transport" -- this is intentional but creates per-request overhead. May be an artifact of early implementation choices that could be optimized. |

## Pattern Statistics
- Total patterns detected: 28
- Architectural: 7
- Design: 17
- Anti-patterns: 6
