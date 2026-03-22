# Shared Memory

Common rules for all agents.

## Rules

- Credentials live in `pass` under `kordinate/`. Agent auth locks live in `profile/locks/`.
- Follow the project's existing patterns — don't introduce new libraries, frameworks, or conventions
- All `.md` files are protected — only the scribe agent may edit them
- Commit with `[<your-name>]` in the message
- Project-specific artifacts go in the project repo, not kordinate
- Only the deployer may run kubectl write operations
- Only the sauron may use Grafana MCP tools
- `mcp__beorn__delegate` spawns a beorn with any agent's skin — use for inter-agent communication at any depth

## Kords

When you need information outside your expertise, use kords (coordination agreements):

| Need to know about | Kord |
|---|---|
| Cluster state, deployments, networking, infrastructure architecture | `/consult deployer` (default-deployer) |
| Metrics, health checks, dashboards, log events, alerting | `/consult sauron` (default-sauron) |
| Design patterns, component topology, data flow, failure modes | `/consult designer` (default-designer) |
| Document templates, formatting conventions | `/consult scribe` (default-scribe) |
| Architecture review for deployment/monitoring changes | `/consult pattern-review` |
| Monitoring impact of infrastructure changes | `/consult monitoring-impact` |

## Memory

Two axes — **scope** (global/project) and **mutability** (static/dynamic):

| | Static (pre-defined structure) | Dynamic (free-form) |
|---|---|---|
| **Global** | `memory/static/` | `memory/dynamic/` |
| **Project** | `<repo>/<you>/static/` | `<repo>/<you>/dynamic/` |

Static holds content with pre-defined structure (manifests, dashboards, pattern catalogs). Dynamic is for agent-managed notes and findings. The linking layer symlinks `.claude/agent-memory/<you>/` to `<repo>/<you>/dynamic/` — write through the symlink, it lands in the right place.
