# installer/

Bootstrap and linking scripts for kordinate.

## Scripts

| Script | Purpose |
|--------|---------|
| `kordinate-cli` | Main CLI: `init`, `join`, `hydrate`, `export`, `import` |
| `link.sh` | Creates symlinks from Claude Code conventions to kordinate sources |
| `lib.sh` | Shared utilities: colors, logging, kubectl resolver (sourced by other scripts) |
| `auth-check.sh` | Workstation auth setup: GPG, pass, GitHub, Tailscale, Claude credentials |

## Links

Managed by `link.sh`. The mapping decouples agent conventions from kordinate's internal structure. If kordinate reorganizes, update the mapping — the agent sees the same paths.

```
┌─────────────┐      link.sh       ┌──────────────┐
│  kordinate/  │ ──── mapping ────► │  ~/.claude/   │
│  (repo)      │                    │  (agent sees) │
└─────────────┘                    └───────┬──────┘
                                           │
                                    ┌──────▼──────┐
                                    │  Claude Code │
                                    │  Cursor      │
                                    │  Copilot     │
                                    │  ...         │
                                    └─────────────┘
```

Kordinate can reorganize freely. The agent sees stable paths. Only the mapping changes.

### Claude Code conventions

Claude Code discovers these by convention at `~/.claude/`:

| Convention (at `~/.claude/`) | Kordinate source | Purpose |
|------------------------------|------------------|---------|
| `CLAUDE.md` | `kordinate/AGENT.md` | Global agent guidelines |
| `settings.json` | `kordinate/profile/settings.json` | Hooks, permissions, settings |
| `keybindings.json` | `kordinate/profile/keybindings.json` | Keyboard shortcuts |
| `.mcp.json` | `kordinate/profile/mcp.json` | MCP server config (encrypted) |
| `agents/` | `kordinate/agents/` | Agent definitions + commands |
| `commands/` | `kordinate/commands/` | Shared slash commands |

### Kordinate internal links

These are NOT Claude Code conventions — they're linked into `~/.claude/` so that hooks, agent docs, and scripts can reference them at stable paths:

| Link (at `~/.claude/`) | Kordinate source | Why |
|-------------------------|------------------|-----|
| `hooks/` | `kordinate/hooks/` | Referenced by `settings.json` with `$HOME/.claude/hooks/` paths |
| `profile/` | `kordinate/profile/` | Hooks read locks at `$HOME/.claude/profile/locks/` |
| `agent-memory/` | `kordinate/agents/memory/` | Agent docs reference `~/.claude/agent-memory/<name>/` |
| `.gitattributes` | `kordinate/.gitattributes` | git-crypt needs it at repo root (when repo is at `~/.claude/`) |

### External resources

| Link (relative to repo) | Target | Purpose |
|--------------------------|--------|---------|
| `kordinate/profile/keystore` | `~/.password-store/kordinate/` | GPG-encrypted credential store (`pass`) |

### Changing the mapping

To reorganize kordinate internals (e.g., move `agent-memory/` into `agents/`):

1. Move the files within `kordinate/`
2. Update the `CLAUDE_LINKS` array in `link.sh` (e.g., `"agent-memory:kordinate/agents/memory"`)
3. Re-run `./installer/link.sh`

Claude Code sees the same paths at `~/.claude/` — no hook, settings, or agent doc changes needed.

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
