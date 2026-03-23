# Root

The orchestrator. Root is the user's existing agent — Claude Code, Codex, Cursor, or any compatible runtime. It defines the team, and all subagents inherit its rules, commands, and hooks.

## Linking

Kordinate is runtime-agnostic. Agent files live at `~/.kord/` in kordinate's format. The **linking layer** converts them to whatever the runtime expects — it's the only part that changes when switching runtimes.

### Claude Code

Claude Code reads these files from `~/.claude/`:

| `~/.claude/` path | Purpose | Writable by Claude? |
|-------------------|---------|:-------------------:|
| `CLAUDE.md` | Root system prompt — inherited by all subagents | no |
| `agents/<name>.md` | Subagent identity | no |
| `commands/*.md` | Slash commands | no |
| `settings.json` | Hooks, permissions, plugins | yes |
| `.mcp.json` | MCP server configuration | yes |
| `keybindings.json` | Key bindings | yes |
| `agent-memory/<name>/` | Agent writable memory | yes |

Claude Code also manages its own files (`.credentials.json`, `projects/`, `sessions/`, `history.jsonl`, etc.) — the linker never touches these.

**Kordinate fills these from `~/.kord/`:**

| `~/.claude/` | `~/.kord/` source | Transform |
|-------------|-------------------|-----------|
| `CLAUDE.md` | `root/identity.md` + `team/manifest.md` | rename + merge |
| `agents/<name>.md` | `<agent>/identity.md` | rename, generate frontmatter |
| `commands/*.md` | `root/commands/*.md` | copy |
| `settings.json` | `settings.json` | copy |
| `.mcp.json` | `mcp.json` | rename |
| `keybindings.json` | `keybindings.json` | copy |
| `agent-memory/<name>/` | `<agent>/memory/` | restructure |

No symlinks. Claude Code works with real files. `~/.kord/` is the portable format.

### How Linking Works

1. Read each file in `~/.kord/`
2. Check frontmatter for memory properties (structured, on-demand, owner, scope, expiry)
3. Apply defaults where no frontmatter exists
4. Transform and copy to the paths the runtime expects

### Adding a Runtime

To support a new runtime (Codex, Cursor, etc.), create a new link script that maps kordinate's structure to that runtime's expected paths. The `~/.kord/` files stay the same — only the linking changes.
