# installer/

Bootstrap and linking scripts for kordinate.

## Scripts

| Script | Purpose |
|--------|---------|
| `kordinate-cli` | Main CLI: `init`, `join`, `hydrate`, `export`, `import` |
| `link.sh` | Creates symlinks so Claude Code discovers `kordinate/` at `~/.claude/` |
| `lib.sh` | Shared utilities: colors, logging, kubectl resolver (sourced by other scripts) |
| `auth-check.sh` | Workstation auth setup: GPG, pass, GitHub, Tailscale, Claude credentials |

## Links

Managed by `link.sh`. These symlinks bridge kordinate's framework into locations that Claude Code and other tools expect.

### Claude Code discovery

Created at `~/.claude/` root so Claude Code finds its convention files:

| Link | Target | Why |
|------|--------|-----|
| `~/.claude/CLAUDE.md` | `kordinate/CLAUDE.md` | Global agent guidelines |
| `~/.claude/settings.json` | `kordinate/settings.json` | Hooks, permissions, settings |
| `~/.claude/keybindings.json` | `kordinate/keybindings.json` | Keyboard shortcuts |
| `~/.claude/.mcp.json` | `kordinate/.mcp.json` | MCP server config |
| `~/.claude/agents` | `kordinate/agents` | Agent definitions |
| `~/.claude/commands` | `kordinate/commands` | Slash commands |
| `~/.claude/hooks` | `kordinate/hooks` | Safety guardrail hooks |
| `~/.claude/profile` | `kordinate/profile` | Site-specific config |
| `~/.claude/agent-memory` | `kordinate/agent-memory` | Cross-project knowledge |

### External resources

Created inside `kordinate/profile/` to connect external stores:

| Link | Target | Why |
|------|--------|-----|
| `profile/keystore` | `~/.password-store/kordinate/` | GPG-encrypted credential store (`pass`) |
| `profile/mcp.json` | `../.mcp.json` | MCP config lives at framework root, profile provides alias |

## Usage

### Fresh install

```bash
git clone <repo-url> ~/kordinate
cd ~/kordinate
./installer/link.sh
./installer/kordinate-cli init
```

### After clone (existing cluster)

```bash
git clone <repo-url> ~/kordinate
cd ~/kordinate
git-crypt unlock          # decrypt profile/
./installer/link.sh       # create symlinks
./installer/kordinate-cli hydrate
```
