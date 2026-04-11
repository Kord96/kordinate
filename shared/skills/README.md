# Global Skills

Skills available to all agents, not owned by any single agent.

| Skill | Command | Purpose |
|-------|---------|---------|
| [boot](boot/SKILL.md) | `/boot` | Load memory and shared protocols on spawn — run before starting any task |
| [authenticate](authenticate/SKILL.md) | `/authenticate` | Copy lock file for guarded operations — authenticate once per task |
| [integrate](integrate/SKILL.md) | `/integrate` | Explicitly reconcile session branches with main and clean up stale worktrees |
| [publish](publish/SKILL.md) | `/publish` | Push the current branch explicitly and optionally prepare it for review |
| [session](session/SKILL.md) | `/session` | List worktree-backed sessions, show sync state, and print resume/create commands |
| [validate-output](validate-output/SKILL.md) | `/validate-output` | Run an agent-owned validator against an output directory and return a completion token |
| [sanitize](sanitize/SKILL.md) | `/sanitize` | Classify config, credentials, and memory and route each part to the right destination |

`/session` is backed by the legacy workstation helper `agents/charon/skills/bootstrap/images/workstation/bin/legacy/session-status` for operational listing and control-plane output.
Agent discovery and delegation now live behind the central `kord` MCP/API surface rather than a shared repo skill.
| [improve](improve/SKILL.md) | `/improve` | Improve skills, agents, or the whole team — run evals, benchmark, iterate, and optimize |
| [install](install/SKILL.md) | `/install` | Install or reinstall kordinate — creates ~/.kord/, links runtime, optionally bootstraps infra |
