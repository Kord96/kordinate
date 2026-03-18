# Link Mapping

Kordinate's framework lives in `~/kordinate/kordinate/`. Claude Code expects its files at `~/.claude/`. The linking layer bridges them — `installer/link.sh` creates symlinks and copies so Claude Code finds everything where it expects, while the repo stays agent-agnostic.

## Claude Code native

Paths that Claude Code discovers by convention:

### Symlinked

| At `~/.claude/` | Points to | Purpose |
|------------------|-----------|---------|
| `agents/` | `kordinate/agents/` | Agent definitions + commands |
| `commands/` | `kordinate/commands/` | Shared slash commands |
| `settings.json` | `kordinate/settings.json` | Hook registrations, permissions |
| `keybindings.json` | `kordinate/profile/keybindings.json` | Keyboard shortcuts |
| `.mcp.json` | `kordinate/profile/mcp.json` | MCP server config |
| `agent-memory/<agent>/` | `kordinate/agents/<agent>/memory/dynamic/` | Auto-managed memory |

### Copied (renamed)

| At `~/.claude/` | Source in repo |
|------------------|----------------|
| `CLAUDE.md` | `kordinate/agents/AGENT.md` |
| `agents/<agent>/CLAUDE.md` | `kordinate/agents/<agent>/AGENT.md` |

Copied on `link.sh deploy`, synced back on `link.sh sync`.

## Kordinate-specific

Paths that Claude Code doesn't know about — linked so kordinate's hooks and scripts resolve at stable `~/.claude/` paths:

| At `~/.claude/` | Points to | Used by |
|------------------|-----------|---------|
| `hooks/` | `kordinate/hooks/` | `settings.json` references `$HOME/.claude/hooks/` |
| `profile/` | `kordinate/profile/` | Hooks read locks at `profile/locks/` |

## External

| Link | Target | Purpose |
|------|--------|---------|
| `kordinate/profile/keystore/` | `~/.password-store/kordinate/` | GPG credential store (`pass`) |
