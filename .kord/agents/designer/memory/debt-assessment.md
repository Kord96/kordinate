---
description: Technical debt assessment for kordinate project
generated: 2026-03-28
project: kordinate
---
# Technical Debt Assessment

## Overall Grade: C (68/100)

## Summary

Kordinate is architecturally well-designed with clean module boundaries, strong RBAC patterns, and pragmatic use of design patterns for a bash-heavy orchestration platform. However, it carries significant debt in testing (zero project-level test coverage), security (critical command injection in the MCP server), and observability of its own components. The absence of CI/CD beyond docs deployment means all quality gates are manual or agent-driven, creating fragility as the platform grows.

## Dimension Scores

| Dimension | Weight | Score | Grade | Key Issues |
|-----------|--------|-------|-------|------------|
| Code Structure | 25% | 78 | B | Files well-sized (92-582 LOC). Clear module boundaries. Minor lava flow in per-request MCP server instantiation. Shell-heavy architecture limits refactoring safety. |
| Dependency Health | 20% | 75 | B | No circular dependencies. Agents communicate only via kords/beorn. Shared PVC is a coupling risk. Several unpinned container images (`latest` tags). Python3 as implicit dependency in shell paths. |
| API Quality | 15% | 52 | D | Critical command injection in `checkExpiry`. No authentication on MCP server. No concurrency limits. Incomplete input validation (unbounded string lengths). Error message disclosure risk. |
| Configuration Management | 15% | 72 | C | Config spread across 4+ files in 3 formats (YAML, JSON, Markdown). Field-level ACL on config.yaml is sophisticated. Secret management via `pass`/GPG is functional but single-point-of-failure. git-crypt for .mcp.json adds key management burden. |
| Testing & Safety | 10% | 25 | F | Zero project-level tests. One integration test script (installer/test/install.sh) exists but is manual k3d-based, not CI-integrated. No unit tests for server.js, guard.sh, or any hook. Single CI workflow (docs deploy only). No automated rollback beyond K8s native. |
| Observability | 10% | 65 | C | Good infrastructure observability (Prometheus, Loki, Grafana, Alloy). Beorn has structured logging. But no metrics from beorn itself (request counts, latencies, error rates). No alerting rules visible. Agent invocations are log-only with no tracing. |
| Documentation | 5% | 80 | B | IDENTITY.md per agent, SKILL.md per skill, contract.md per kord. CLAUDE.md provides onboarding. mkdocs site exists. Missing: architecture decision records, deployment runbook, troubleshooting guide. |

## Violations

### CRITICAL
| Issue | Location | Impact | Remediation |
|-------|----------|--------|-------------|
| Command injection in `checkExpiry` | `server.js:218` | User-controlled `message` passed to `execSync()` shell string. `JSON.stringify()` wraps in double quotes but shell interprets `$(...)` and backticks. Attacker can execute arbitrary commands. | Replace `execSync(bash "..." ${JSON.stringify(message)})` with `execFileSync('bash', [expiryScript, message], {...})` to avoid shell interpretation. |
| Zero test coverage | Project-wide | No automated verification of any business logic. Regressions in guard.sh, server.js, or hooks are undetectable until runtime failure. | Add unit tests for guard.sh (BATS), server.js (vitest/jest), and kord-expiry.sh. Target critical paths first: permission checks, agent invocation, cache expiry. |
| No CI/CD pipeline for code | `.github/workflows/` | Only docs deployment exists. No linting, testing, security scanning, or build validation on PRs or merges. | Add a CI workflow: shellcheck for bash, eslint for JS, unit tests, and basic security scanning (e.g., `npm audit`). |

### RECOMMENDED
| Issue | Location | Impact | Remediation |
|-------|----------|--------|-------------|
| No authentication on MCP server | `server.js` (all endpoints) | Any pod in the cluster can invoke any agent with any prompt. Lateral movement risk if cluster is compromised. | Add a NetworkPolicy restricting ingress to known clients. Consider ServiceAccount token validation. |
| No concurrency limit on agent spawning | `server.js:128-165` | Unbounded concurrent subprocess spawning can OOM the 1Gi pod with 2-3 simultaneous requests. | Track active subprocess count, reject with 429 when at capacity (e.g., max 2 concurrent). |
| Unpinned container images | Multiple manifests | `minio/minio:latest`, `cloudflare/cloudflared:latest`, `ghcr.io/tailscale/tailscale:latest`, `grafana/grafana-image-renderer:latest` use `latest` tags. Upstream breaking changes can cause silent failures. | Pin all images to specific digests or version tags. |
| Stringly-typed command parsing in guard.sh | `guard.sh:140-198` | Git push and kubectl command detection uses regex/grep on shell strings. Edge cases in quoting, command chaining, or aliases could bypass guards. | Consider structured command analysis or a more robust parsing approach. Document known bypass vectors. |
| Single PVC failure domain | `kord` PVC (20Gi RWX) | All pods share one Longhorn PVC. Corruption or Longhorn failure takes down the entire platform. No automated backups visible. | Add PVC backup automation (Velero or Longhorn snapshots on schedule). Document recovery procedures. |
| Swallowed exceptions in agent discovery | `server.js:42,50,102` | Silent `catch {}` blocks make debugging agent loading failures difficult. | Log caught errors at debug level. Add a diagnostic mode that surfaces discovery issues. |
| Error message disclosure | `server.js:383` | Raw `e.message` in JSON-RPC error response could expose file paths or subprocess details. | Sanitize error responses for clients; log full details server-side only. |
| No input length limits on MCP tools | `server.js:237-239` | `prompt` and `message` are unbounded Zod strings. Express 1MB body limit is the only ceiling. | Add `.max(100000)` to prompt/message Zod schemas. |

### MINOR
| Issue | Location | Impact | Remediation |
|-------|----------|--------|-------------|
| Magic numbers | `server.js:144` (300000ms), `kord-expiry.sh:57-58` (0.05, 0.30, 7d) | Hardcoded timeouts and thresholds reduce configurability. | Extract to named constants or config. |
| Config sprawl across formats | `config.yaml`, `settings.json`, `topology.yaml`, `KORD.json` | Four config files in three formats require understanding multiple schemas to reason about the system. | Document the config hierarchy and purpose of each file. Consider consolidating where practical. |
| Per-request MCP server instantiation | `server.js:365-386` | Each POST /mcp creates a new McpServer + transport + tool registration. Adds latency and GC pressure. | Investigate connection-scoped or reusable server instances if MCP SDK supports it. |
| `kord_name` path traversal risk | `server.js:205` | `kord_name` used in filesystem path without pattern validation. `path.join` normalizes `..` but no explicit sanitization. | Validate `kord_name` against `/^[a-z0-9-]+$/`. |
| Shell injection surface in guard.sh | `guard.sh:51` | Python inline receives shell variables via environment. Safer than interpolation but warrants monitoring. | Already mitigated by env-based passing. Document the security boundary. |
| Installer embeds Python in bash | `kordinate-cli:43-54,99-107,171-187,419-444` | Multiple inline Python scripts for YAML parsing. Fragile if python3 or PyYAML is missing. | Add explicit python3+PyYAML check at installer start. Consider a pure-bash YAML parser for simple reads. |

## Prioritized Recommendations

Ranked by severity x blast-radius x (1/effort):

| # | Recommendation | Severity | Blast Radius | Effort | Priority Score |
|---|---------------|----------|-------------|--------|---------------|
| 1 | Fix command injection in `checkExpiry` (server.js:218) | Critical | High (any kord request) | Trivial (1 line) | 10.0 |
| 2 | Add CI workflow (lint + shellcheck + npm audit) | High | Entire codebase | Small (1-2 hours) | 8.0 |
| 3 | Add unit tests for guard.sh permission logic | High | All write/bash operations | Medium (1-2 days) | 6.5 |
| 4 | Add concurrency limit to beorn agent spawning | High | MCP server stability | Small (30 min) | 6.0 |
| 5 | Pin all container images to version tags | Medium | All deployments | Small (1 hour) | 5.5 |
| 6 | Add NetworkPolicy for agent-factory | Medium | Cluster security | Small (30 min) | 5.0 |
| 7 | Add unit tests for server.js (delegate, kord, status tools) | High | MCP server correctness | Medium (1-2 days) | 5.0 |
| 8 | Add input validation limits to MCP tool schemas | Medium | MCP server resilience | Trivial (5 min) | 4.5 |
| 9 | Sanitize JSON-RPC error responses | Low | Information disclosure | Trivial (10 min) | 3.5 |
| 10 | Add PVC backup automation | Medium | Data durability | Medium (half day) | 3.0 |
| 11 | Add beorn metrics endpoint (request count, latency, errors) | Medium | Observability | Small (1-2 hours) | 2.5 |
| 12 | Document config hierarchy and relationships | Low | Developer onboarding | Small (1 hour) | 2.0 |

## Debt Clusters

**Cluster 1: MCP Server Security (Items 1, 4, 6, 8, 9)**
The beorn MCP server has multiple interrelated security and resilience gaps. The command injection is the most urgent, but adding concurrency limits, input validation, NetworkPolicy, and error sanitization should be done as a single hardening pass. Estimated total effort: 1 day.

**Cluster 2: Testing Infrastructure (Items 2, 3, 7)**
Zero test coverage and no CI pipeline form a compound risk. Adding CI first (item 2) creates the framework; then guard.sh tests (item 3) and server.js tests (item 7) provide the highest-value coverage. The existing `installer/test/install.sh` integration test should be wired into CI as well. Estimated total effort: 3-4 days.

**Cluster 3: Infrastructure Resilience (Items 5, 10)**
Unpinned images and unbackedPVCs are independent risks but share the theme of production reliability. Both should be addressed in a single infrastructure hardening sprint. Estimated total effort: 1 day.

**Cluster 4: Observability Gap (Item 11)**
Beorn logs are structured but there are no Prometheus metrics from the MCP server itself. Given that the observability stack (Prometheus, Grafana, Alloy) is already deployed, adding a `/metrics` endpoint to beorn and a Grafana dashboard is low-effort, high-value. Estimated total effort: half day.

## Trend Indicators

**Debt is slowly growing.** Evidence:

- **Growing complexity**: Recent commits show iterative skill improvements across multiple agents (alfred, warden, scribe, sauron), indicating active feature development without corresponding test additions.
- **No test debt reduction**: There is no evidence of any test-related commits in recent history. The testing gap is widening as more skills and kord contracts are added.
- **Architecture is stabilizing**: The core patterns (hook system, guard.sh, beorn, kord contracts) appear mature and well-understood. The 28 detected patterns vs. 6 anti-patterns ratio is healthy.
- **Security debt is static**: The command injection in `checkExpiry` and missing authentication have likely been present since initial implementation. They are not growing but represent latent risk.
- **Config sprawl is contained**: The field-level ACL system (config-acl.yaml) and KORD.json catalog show intentional governance of configuration, preventing uncontrolled sprawl.

**Prognosis**: Without CI/CD and testing investment, the platform will accumulate regression risk as agents and skills continue to evolve. The architectural foundations are sound, so the debt is addressable with focused effort on the three critical items (command injection fix, CI pipeline, initial test coverage).
