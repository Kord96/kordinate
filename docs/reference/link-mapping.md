# Link Mapping

Kordinate's framework lives in `~/kordinate/kordinate/`. Claude Code expects its files at `~/.claude/`. The linking layer (`installer/link.sh`) bridges them.

## Direct (same structure)

| Claude Code | Kordinate |
|-------------|-----------|
| `agents/` | `agents/` |
| `commands/` | `commands/` |

## Remapped (different location)

| Claude Code | Kordinate | Why different |
|-------------|-----------|---------------|
| `settings.json` | `settings.json` (framework root) | Framework config, not inside agents/ |
| `keybindings.json` | `profile/keybindings.json` | Site-specific |
| `.mcp.json` | `profile/mcp.json` | Site-specific, encrypted |
| `agent-memory/<agent>/` | `agents/<agent>/memory/dynamic/` | Memory colocated with agent, not separate tree |

## Renamed (different filename)

Kordinate uses `AGENT.md`, Claude Code expects `CLAUDE.md`. Copied on `link.sh deploy`, synced back on `link.sh sync`:

| Claude Code | Kordinate |
|-------------|-----------|
| `CLAUDE.md` | `agents/AGENT.md` |
| `agents/<agent>/CLAUDE.md` | `agents/<agent>/AGENT.md` |

## Kordinate-specific links

Not Claude Code conventions — linked so hooks and scripts resolve at stable paths:

| At `~/.claude/` | Kordinate | Used by |
|------------------|-----------|---------|
| `hooks/` | `hooks/` | `settings.json` references `$HOME/.claude/hooks/` |
| `profile/` | `profile/` | Hooks read locks at `profile/locks/` |

## External

| Link | Target | Purpose |
|------|--------|---------|
| `profile/keystore/` | `~/.password-store/kordinate/` | GPG credential store (`pass`) |
