# Claude Code Native Paths

Level 3 resource for the remember skill.

## Full Claude Code Filesystem

| Path | Purpose | Managed by |
|------|---------|-----------|
| `~/.claude/CLAUDE.md` | Global system prompt — loaded into main session, NOT inherited by subagents | Developer (curated) |
| `.claude/CLAUDE.md` | Project system prompt — same behavior, project-scoped | Developer (curated) |
| `~/.claude/agents/<name>.md` | Subagent identity — frontmatter + body as spawn prompt | Scribe (via onboard) |
| `~/.claude/agent-memory/<name>/MEMORY.md` | Global subagent memory — 200 lines auto-loaded | Scribe (via remember) |
| `.claude/agent-memory/<name>/MEMORY.md` | Project subagent memory — same behavior | Scribe (via remember) |
| `~/.claude/projects/<project>/memory/MEMORY.md` | Main session auto memory — index + topic files | Claude (auto) |
| `~/.claude/projects/<project>/memory/*.md` | Main session topic files — read on-demand | Claude (auto) |
| `~/.claude/skills/<name>/SKILL.md` | Skills — discovered at startup, loaded when triggered | Developer / Scribe |
| `~/.claude/settings.json` | Permissions, hooks, env vars | Developer |
| `~/.claude/.mcp.json` | MCP server configuration | Developer |
| `~/.claude/rules/*.md` | Path-scoped rules — load when matching file globs | Developer |

## Key Behaviors

- Subagent MEMORY.md: single flat file, 200-line auto-load, no topic files.
- Main session auto memory: managed by Claude itself — do not write to it directly.
- CLAUDE.md: developer-written, curated. Claude does not auto-write to it.
- Subagents do NOT inherit CLAUDE.md, rules, skills, or conversation history.
- Write concise summaries to Claude native MEMORY.md. Detailed notes stay in kordinate topic files.
