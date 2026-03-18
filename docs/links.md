# Link Mapping

Kordinate's framework lives in `~/kordinate/kordinate/`. Claude Code expects its files at `~/.claude/`. The linking layer bridges them — `installer/link.sh` creates symlinks and copies so Claude Code finds everything at the paths it expects, while the repo stays agent-agnostic.

## Symlinks

Directories that Claude Code reads/writes through directly:

| At `~/.claude/` | Points to | Purpose |
|------------------|-----------|---------|
| `agents/` | `kordinate/agents/` | Agent definitions, commands, memory |
| `commands/` | `kordinate/commands/` | Shared slash commands |
| `hooks/` | `kordinate/hooks/` | Safety hooks (referenced by settings.json) |
| `profile/` | `kordinate/profile/` | Site config, locks, keystore |
| `settings.json` | `kordinate/settings.json` | Hook registrations |
| `keybindings.json` | `kordinate/profile/keybindings.json` | Keyboard shortcuts |
| `.mcp.json` | `kordinate/profile/mcp.json` | MCP server config |

Per-agent auto-memory (Claude writes here), for each agent:

| At `~/.claude/` | Points to |
|------------------|-----------|
| `agent-memory/<agent>/` | `kordinate/agents/<agent>/memory/dynamic/` |

## Copies

Files that need renaming (`AGENT.md` → `CLAUDE.md`). Copied on `link.sh deploy`, synced back on `link.sh sync`:

| At `~/.claude/` | Source in repo |
|------------------|----------------|
| `CLAUDE.md` | `kordinate/agents/AGENT.md` |
| `agents/<agent>/CLAUDE.md` | `kordinate/agents/<agent>/AGENT.md` |

## External

| Link | Target | Purpose |
|------|--------|---------|
| `kordinate/profile/keystore/` | `~/.password-store/kordinate/` | GPG credential store (`pass`) |
