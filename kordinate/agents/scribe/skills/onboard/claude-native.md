# Claude Code Native Paths

Level 3 resource for the onboard skill.

## Full Claude Code Filesystem

| Path | Purpose | Managed by |
|------|---------|-----------|
| `~/.claude/CLAUDE.md` | Global system prompt — loaded into main session, NOT inherited by subagents | Developer (curated) |
| `.claude/CLAUDE.md` | Project system prompt — same behavior, project-scoped | Developer (curated) |
| `~/.claude/agents/<name>.md` | Subagent identity — frontmatter + body as spawn prompt | Scribe (via onboard) |
| `~/.claude/agent-memory/<name>/MEMORY.md` | Global subagent memory — 200 lines auto-loaded | Scribe (via remember) |
| `.claude/agent-memory/<name>/MEMORY.md` | Project subagent memory — same behavior | Scribe (via remember) |
| `~/.claude/projects/<project>/memory/MEMORY.md` | Main session auto memory — index + topic files | Claude (auto) |
| `~/.claude/skills/<name>/SKILL.md` | Skills — discovered at startup, loaded when triggered | Developer / Scribe |
| `~/.claude/settings.json` | Permissions, hooks, env vars | Developer |
| `~/.claude/.mcp.json` | MCP server configuration | Developer |

## Agent File Details

`~/.claude/agents/<name>.md`

- Filename must match the `name` field in frontmatter. Flat file, not a directory.
- Discovered at session start (restart required if added mid-session).
- Spawnable via `@agent-name` mention or programmatically via the Agent tool.
- Frontmatter controls: tools, model, memory scope, hooks, skills.
- Markdown body becomes the subagent's system prompt.
- Subagent does NOT inherit CLAUDE.md, rules, or parent skills.
