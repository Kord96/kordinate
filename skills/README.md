# Global Skills

Skills available to all agents, not owned by any single agent.

| Skill | Command | Purpose |
|-------|---------|---------|
| [boot](boot/SKILL.md) | `/boot` | Load memory and shared protocols on spawn — run before starting any task |
| [authenticate](authenticate/SKILL.md) | `/authenticate` | Copy lock file for guarded operations — authenticate once per task |
| [kord](kord/SKILL.md) | `/kord <question>` | Route requests to other agents through kord contracts |
| [merge](merge/SKILL.md) | `/merge` | Merge session branches into main and clean up stale worktrees |
| [install](install/SKILL.md) | `/install` | Install or reinstall kordinate — creates ~/.kord/, links runtime, optionally bootstraps infra |
