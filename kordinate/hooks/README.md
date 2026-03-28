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
| Bash `git push` to test/prod | any | `/tmp/.charon-auth` | Use `/roll` |
| Bash `kubectl` write ops | mutating verbs | `/tmp/.charon-auth` | Use `/roll` or `/bootstrap` |
| Bash `kubectl` workstation/master/drain/cordon | any | **always blocked** | Never allowed |
| Bash Grafana API calls | any | `/tmp/.sauron-auth` | Use `/authenticate` as sauron |
| `mcp__grafana*` | any | `/tmp/.sauron-auth` | Use `/authenticate` as sauron |

Non-curated, non-templated `.kord/` files are allowed without scribe auth.

### Authentication

Guards check lock files via `/authenticate`. The flow:

1. Agent runs `/authenticate` → copies `profile/locks/<agent>` to `/tmp/.<agent>-auth`
2. Guard compares `/tmp/.<agent>-auth` contents against `profile/locks/<agent>`
3. Match → allow. No match or missing → deny.

## Automation

| Hook | Purpose | Trigger |
|------|---------|---------|
| [agent-memory.sh](agent-memory.sh) | Regenerate agent MEMORY.md on spawn (hash-based caching) | Agent (PreToolUse) |
