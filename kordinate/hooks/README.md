# Hooks

Pre/post-tool hooks that enforce domain boundaries and automate workflows. Configured in `settings.json`.

## Unified Guard

[guard.sh](guard.sh) is the single guard script for all domain enforcement. It routes based on the tool being used and checks authentication lock files.

### Rules

| Trigger | Condition | Auth | Deny message |
|---------|-----------|------|-------------|
| Write/Edit to `*/.kord/*` | `curated: true` in KORD.json | `/tmp/.scribe-auth` | Use `/kord remember` |
| Write/Edit to `*/dashboards/*.json` | any | `/tmp/.sauron-auth` | Use `/authenticate` as sauron |
| Bash `git push` to main | branch has diverged | — | Use `/merge` to rebase |
| Bash `git push` to test/prod | any | `/tmp/.deployer-auth` | Use `/infra roll` |
| Bash `kubectl` write ops | mutating verbs | `/tmp/.deployer-auth` | Use `/infra` |
| Bash `kubectl` workstation/master/drain/cordon | any | **always blocked** | Never allowed |
| Bash Grafana API calls | any | `/tmp/.sauron-auth` | Use `/authenticate` as sauron |
| `mcp__grafana*` | any | `/tmp/.sauron-auth` | Use `/authenticate` as sauron |

Non-curated, non-templated `.kord/` files are allowed without scribe auth.

### Authentication

Guards check lock files via `/authenticate`. The flow:

1. Agent runs `/authenticate` → copies `profile/locks/<agent>` to `/tmp/.<agent>-auth`
2. Guard compares `/tmp/.<agent>-auth` contents against `profile/locks/<agent>`
3. Match → allow. No match or missing → deny.

## Dev Sync

[dev-sync.sh](../../hooks/dev-sync.sh) is a git `post-commit` hook for kordinate developers. It lives in the repo-root `hooks/` directory (not in this package directory) because it is a dev tool, not an installed package file.

| Trigger | Condition | Action |
|---------|-----------|--------|
| git post-commit | `.dev-source` exists and matches repo | Copies changed `kordinate/` files to `$KORDINATE_HOME` |

Activated via `register runtime --dev`. See [dev-sync.md](../agents/scribe/skills/register/dev-sync.md) for full documentation.

## Agent Memory

Agent MEMORY.md files are maintained by Scribe — updated during `/onboard` (link step) and `/kord remember` (write step). No spawn-time hook needed.
