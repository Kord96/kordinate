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
- Only the deployer may use Redis MCP tools

## Consultation Directory

When you need information outside your expertise, consult the right agent:

| Need to know about | Consult |
|---|---|
| Cluster state, deployments, networking, infrastructure architecture | **deployer** |
| Metrics, health checks, dashboards, log events, alerting | **sauron** |
| Design patterns, component topology, data flow, failure modes | **designer** |
| Document templates, formatting conventions | **scribe** |

## Memory

Two axes — **scope** (global/project) and **mutability** (static/dynamic):

| | Static (pre-defined structure) | Dynamic (free-form) |
|---|---|---|
| **Global** | `memory/static/` | `memory/dynamic/` |
| **Project** | `<repo>/<you>/static/` | `<repo>/<you>/dynamic/` |

Static holds content with pre-defined structure (manifests, dashboards, pattern catalogs). Dynamic is for agent-managed notes and findings. The linking layer symlinks `.claude/agent-memory/<you>/` to `<repo>/<you>/dynamic/` — write through the symlink, it lands in the right place.
