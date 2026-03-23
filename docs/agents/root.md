# Root

The orchestrator. Root is the user's existing agent — Claude Code, Codex, Cursor, or any compatible runtime. It defines the team, and all subagents inherit its rules, commands, and hooks.

## Linking

Root is mapped to the runtime's main agent via the linking layer. For Claude Code, this means `identity.md` becomes `CLAUDE.md`.

| `~/.kord/` | `~/.claude/` | Transform |
|-----------|-------------|-----------|
| `root/identity.md` | `CLAUDE.md` | rename |
| `team/manifest.md` | merged into `CLAUDE.md` | append |
| `settings.json` | `settings.json` | copy |
| `keybindings.json` | `keybindings.json` | copy |
| `mcp.json` | `.mcp.json` | rename |

The linking layer is the only part that changes when switching runtimes. Kordinate files stay the same.

### Adding a Runtime

To support a new runtime (Codex, Cursor, etc.), create a new link script that maps kordinate's structure to that runtime's expected paths. The framework files stay the same — only the linking changes.
