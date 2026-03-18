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
┌──────────────┐     link.sh      ┌──────────────┐     ┌──────────────┐
│  kordinate/  │ ─── mapping ───► │  ~/.claude/   │ ◄── │  Claude Code  │
│  (repo)      │                  │  (symlinks)   │     │              │
└──────────────┘                  └──────────────┘     └──────────────┘
```

Kordinate can reorganize freely. Claude Code sees stable paths. Only the mapping changes.

See [LINKS.md](LINKS.md) for the full mapping. To reorganize kordinate internals, update the arrays in `link.sh` and re-run it.

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
