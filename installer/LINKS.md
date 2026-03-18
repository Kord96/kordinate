# Link Mapping

Single source of truth for all symlinks managed by `link.sh`.

## Claude Code conventions

Claude Code discovers these by convention at `~/.claude/`:

| Convention (at `~/.claude/`) | Kordinate source | Purpose |
|------------------------------|------------------|---------|
| `CLAUDE.md` | `kordinate/AGENT.md` | Global agent guidelines |
| `settings.json` | `kordinate/profile/settings.json` | Hooks, permissions, settings |
| `keybindings.json` | `kordinate/profile/keybindings.json` | Keyboard shortcuts |
| `.mcp.json` | `kordinate/profile/mcp.json` | MCP server config (encrypted) |
| `agents/` | `kordinate/agents/` | Agent definitions + commands |
| `commands/` | `kordinate/commands/` | Shared slash commands |

## Kordinate internal

NOT Claude Code conventions — linked into `~/.claude/` so hooks, agent docs, and scripts resolve at stable paths:

| Link (at `~/.claude/`) | Kordinate source | Why |
|-------------------------|------------------|-----|
| `hooks/` | `kordinate/hooks/` | Referenced by `settings.json` with `$HOME/.claude/hooks/` paths |
| `profile/` | `kordinate/profile/` | Hooks read locks at `$HOME/.claude/profile/locks/` |
| `agent-memory/` | `kordinate/agents/memory/` | Agent docs reference `~/.claude/agent-memory/<name>/` |
| `.gitattributes` | `kordinate/.gitattributes` | git-crypt encryption rules |

## External resources

| Link (relative to repo) | Target | Purpose |
|--------------------------|--------|---------|
| `kordinate/profile/keystore` | `~/.password-store/kordinate/` | GPG-encrypted credential store (`pass`) |
