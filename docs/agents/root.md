# Root

The orchestrator. Root is the user's existing agent — Claude Code, Codex, Cursor, or any compatible runtime. It defines the team, and all subagents inherit its rules, commands, and hooks.

## Linking

Kordinate is runtime-agnostic. Agent files live at `~/.kord/` in kordinate's format. The **linking layer** converts them to whatever the runtime expects — it's the only part that changes when switching runtimes.

### Claude Code

Claude Code reads from `~/.claude/`. Some files are direct copies:

| `~/.claude/` | `~/.kord/` | Transform |
|-------------|-----------|-----------|
| `settings.json` | `settings.json` | copy |
| `.mcp.json` | `mcp.json` | rename |
| `keybindings.json` | `keybindings.json` | copy |

These require linking:

| `~/.claude/` | Purpose | `~/.kord/` source | Transform |
|-------------|---------|-------------------|-----------|
| `CLAUDE.md` | Root system prompt — inherited by all subagents | `root/identity.md` + `team/manifest.md` | rename + merge |
| `agents/<name>.md` | Subagent identity | `<agent>/identity.md` | rename, generate frontmatter |
| `commands/*.md` | Slash commands | `root/commands/*.md` | copy |
| `agent-memory/<name>/` | Agent writable memory | `<agent>/memory/` | restructure |

No symlinks. Claude Code works with real files. `~/.kord/` is the portable format.

### How Linking Works

1. Read each file in `~/.kord/`
2. Check frontmatter for memory properties (structured, on-demand, owner, scope, expiry)
3. Apply defaults where no frontmatter exists
4. Transform and copy to the paths the runtime expects

### Adding a Runtime

To support a new runtime (Codex, Cursor, etc.), create a new link script that maps kordinate's structure to that runtime's expected paths. The `~/.kord/` files stay the same — only the linking changes.
