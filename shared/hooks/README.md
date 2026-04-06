# Hooks

Hooks that enforce domain boundaries. Configured in `settings.json`.

## Unified Guard

[guard.sh](guard.sh) is the single guard script for all domain enforcement. It routes based on the tool being used and checks authentication lock files.

### Rules

| Trigger | Condition | Auth | Deny message |
|---------|-----------|------|-------------|
| Write/Edit to `*/.kord/*` | protected in `shared/runtime-ownership.yaml` | owner auth | authenticate as the owning agent |
| Write/Edit to `*/dashboards/*.json` | any | `/tmp/.sauron-auth` | Use `/authenticate` as sauron |
| Bash `git push` to main | branch has diverged | — | Use `/integrate` to reconcile |
| Bash `git push` to test/prod | any | `/tmp/.charon-auth` | Use `/infra roll` |
| Bash `kubectl` write ops | mutating verbs | `/tmp/.charon-auth` | Use `/infra` |
| Bash `kubectl` workstation/master/drain/cordon | any | **always blocked** | Never allowed |
| Bash Grafana API calls | any | `/tmp/.sauron-auth` | Use `/authenticate` as sauron |
| `mcp__grafana*` | any | `/tmp/.sauron-auth` | Use `/authenticate` as sauron |

The primary runtime guard no longer depends on the old KORD metadata path and no longer uses the removed KORD compatibility hook.

### Authentication

Guards check lock files via `/authenticate`. The flow:

1. Agent runs `/authenticate` → copies `profile/locks/<agent>` to `/tmp/.<agent>-auth`
2. Guard compares `/tmp/.<agent>-auth` contents against `profile/locks/<agent>`
3. Match → allow. No match or missing → deny.

## Merge-on-push status

Legacy merge-on-push hooks are now disabled. Integration is explicit via `/integrate`.

## Dev Sync

[dev-sync.sh](dev-sync.sh) is a git `post-commit` hook for kordinate developers. It now lives alongside the rest of the shared framework hooks because it is part of the kordinate hook surface.

| Trigger | Condition | Action |
|---------|-----------|--------|
| git post-commit | `.dev-source` exists and matches repo | Copies changed `kordinate/` files to `$KORDINATE_HOME` |

Activated via `register runtime --dev`.

## Validation Lock

Two hooks enforce output quality for any skill that uses warden's `validate-output` pattern.

### validate-lock-hook.sh (PreToolUse on Write/Edit)

Blocks writes to any project memory directory (`memory/projects/*/`) that contains a `.validate-lock` file. The agent sees an error message telling it to fix validation errors — it never knows about the lock mechanism itself.

### validate-post-hook.sh (PostToolUse on Bash)

Detects when an agent runs a `validate_output` script (any skill's validator following the naming convention). Silently re-runs the same validator with `VALIDATE_LOCK=1` to create or remove the lock based on the result.

| Trigger | Condition | Action |
|---------|-----------|--------|
| Write/Edit to `memory/projects/*/` | `.validate-lock` exists | Deny with fix instructions |
| Bash runs `*validate_output*` | script + dir detected | Re-run with `VALIDATE_LOCK=1` to manage lock |

### Validator contract

Any validator script that follows this contract works with the hooks:
1. Named `validate_output.py` or `validate_output.sh`
2. Accepts a directory path as first argument
3. Exits 0 on success, non-zero on failure
4. When `VALIDATE_LOCK=1`: creates `<dir>/.validate-lock` on failure, removes on success

## Agent Memory

Agent MEMORY.md files are updated during `/onboard` (link step) and `write_memory` (write step). No spawn-time hook needed.
