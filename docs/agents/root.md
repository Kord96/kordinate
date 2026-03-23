# Root

The orchestrator. Root is the user's existing agent — Claude Code, Codex, Cursor, or any compatible runtime. It defines the team, and all subagents inherit its rules, commands, and hooks.

## Claude Code

Claude Code reads from two scopes: `~/.claude/` (user — all projects) and `.claude/` (project — committed to repo). The linker targets user scope.

| Path | Purpose |
|------|---------|
| `~/.claude/CLAUDE.md` | Root system prompt — inherited by all subagents |
| `~/.claude/agents/<name>.md` | Subagent identity — flat file, YAML frontmatter + markdown body |
| `~/.claude/agent-memory/<name>/MEMORY.md` | Agent memory — first 200 lines auto-injected at startup |
| `~/.claude/skills/<name>/SKILL.md` | Skills — injected into agent context by name reference |
| `~/.claude/commands/*.md` | Slash commands |
| `~/.claude/settings.json` | Permissions, hooks, env vars |
| `~/.claude/.mcp.json` | MCP server configuration |
| `~/.claude/keybindings.json` | Keyboard shortcuts |

## Linking

Kordinate is runtime-agnostic. Agent files live at `~/.kord/` in a portable format. The **linking layer** converts them to whatever the runtime expects — it's the only part that changes when switching runtimes.

| `~/.claude/` | `~/.kord/` source | Transform |
|-------------|-------------------|-----------|
| `CLAUDE.md` | `root/identity.md` + `team/manifest.md` | merge |
| `agents/<name>.md` | `<agent>/identity.md` | rename, generate frontmatter |
| `agent-memory/<name>/` | `<agent>/memory/` | restructure |
| `skills/<name>/SKILL.md` | `<agent>/skills/` | restructure |
| `commands/*.md` | `root/commands/*.md` | copy |
| `settings.json` | `settings.json` | copy |
| `.mcp.json` | `mcp.json` | rename |
| `keybindings.json` | `keybindings.json` | copy |

No symlinks. Claude Code works with real files. `~/.kord/` is the portable format.

### Adding a Runtime

To support a new runtime (Codex, Cursor, etc.), create a new link script that maps kordinate's structure to that runtime's expected paths. The `~/.kord/` files stay the same — only the linking changes.
