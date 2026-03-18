# Link Mapping

Single source of truth for all links managed by `link.sh`.

## Method

- **Directories** — symlinked. Claude Code reads and writes through them.
- **Renamed files** (AGENT.md → CLAUDE.md) — copied on deploy, synced back before commit.

Run `./installer/link.sh` to deploy. Run `./installer/link.sh sync` to copy changes back.

## Claude Code conventions — symlinked

| Convention (at `~/.claude/`) | Kordinate source | Purpose |
|------------------------------|------------------|---------|
| `settings.json` | `kordinate/settings.json` | Hooks, permissions, settings |
| `keybindings.json` | `kordinate/profile/keybindings.json` | Keyboard shortcuts |
| `.mcp.json` | `kordinate/profile/mcp.json` | MCP server config (encrypted) |
| `agents/` | `kordinate/agents/` | Agent definitions + commands |
| `commands/` | `kordinate/commands/` | Shared slash commands |

## Claude Code conventions — copied (renamed)

| Convention (at `~/.claude/`) | Kordinate source | Direction |
|------------------------------|------------------|-----------|
| `CLAUDE.md` | `kordinate/agents/AGENT.md` | deploy: repo → claude, sync: claude → repo |
| `agents/deployer/CLAUDE.md` | `kordinate/agents/deployer/AGENT.md` | deploy: repo → claude, sync: claude → repo |
| `agents/sauron/CLAUDE.md` | `kordinate/agents/sauron/AGENT.md` | deploy: repo → claude, sync: claude → repo |
| `agents/designer/CLAUDE.md` | `kordinate/agents/designer/AGENT.md` | deploy: repo → claude, sync: claude → repo |
| `agents/scribe/CLAUDE.md` | `kordinate/agents/scribe/AGENT.md` | deploy: repo → claude, sync: claude → repo |

## Kordinate internal — symlinked

| Link (at `~/.claude/`) | Kordinate source | Why |
|-------------------------|------------------|-----|
| `hooks/` | `kordinate/hooks/` | Referenced by `settings.json` with `$HOME/.claude/hooks/` paths |
| `profile/` | `kordinate/profile/` | Hooks read locks at `$HOME/.claude/profile/locks/` |
| `agent-memory/deployer` | `kordinate/agents/deployer/memory/dynamic/` | Auto-memory (encrypted) |
| `agent-memory/sauron` | `kordinate/agents/sauron/memory/dynamic/` | Auto-memory (encrypted) |
| `agent-memory/designer` | `kordinate/agents/designer/memory/dynamic/` | Auto-memory (encrypted) |
| `agent-memory/scribe` | `kordinate/agents/scribe/memory/dynamic/` | Auto-memory (encrypted) |
| `.gitattributes` | `kordinate/.gitattributes` | git-crypt encryption rules |

## External resources — symlinked

| Link (relative to repo) | Target | Purpose |
|--------------------------|--------|---------|
| `kordinate/profile/keystore` | `~/.password-store/kordinate/` | GPG-encrypted credential store (`pass`) |
