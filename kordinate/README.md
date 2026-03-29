# kordinate

Core framework for coordinating specialized AI agents into a team.

## Structure

| Directory | Purpose |
|-----------|---------|
| [agents/](agents/) | Four specialized agents — deployer, designer, sauron, scribe |
| [skills/](skills/) | Global skills available to all agents — boot, authenticate, kord, merge, install |
| [kords/](kords/) | Inter-agent contracts defining how agents consult each other |
| [hooks/](hooks/) | Pre/post-tool enforcement — guards for kubectl, git, Grafana, markdown |
| [shared/](shared/) | Team-wide protocols — auth, credentials, memory |
| [profile/](profile/) | Runtime configuration — cluster config, overlays, locks |
| [lib/](lib/) | Shared utilities — cache, MCP agent server |

## Key Files

- `KORD.json` — Auto-generated index of all agents, memory, kords, and skills
- `KORD.json` — Structured registry used by the runtime
- `settings.json` — Hook configuration and Claude Code plugins
- `CLAUDE.md.example` — Template for user's private instructions
