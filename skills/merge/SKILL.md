---
name: merge
description: Merge session or memory branches into main and clean up stale worktrees.
curated: true
scope: global
---

Merge session branches back into main and garbage-collect stale worktrees left by `claude-session`. Run periodically.

`$ARGUMENTS` — Optional flags and branch names:
- `--memory` — merge `memory/*` branches in `$KORDINATE_HOME` instead of `session/*` branches in the current repo.
- Specific branch name (e.g., `session/w1-logbd` or `memory/agent-abc123`).
- Default (no flag): session branches in current repo.

## Procedure

1. **Discover + classify** — see [discover.md](discover.md).
2. **Merge** branches with changes — see [merge-branches.md](merge-branches.md).
3. **Merge kord branches** — for each merged session branch, check if a matching `session/*` branch exists in `$KORDINATE_HOME`. If so, merge it using the memory branch procedure in [merge-branches.md](merge-branches.md). This is automatic — no `--memory` flag needed.
4. **Cleanup** merged, empty, and stale branches — see [cleanup.md](cleanup.md). Also clean up the corresponding kord branches.
5. **Report**: merged (commits), conflicted (files), cleaned up (empty), skipped (active). Include kord merge results.

## Rules

- Session branches are local only — never push them to remote.
- Never force-push to main — `git push origin HEAD:main` only succeeds on fast-forward.
- Always use detached HEAD in the merge workspace — never checkout named branches.
- Always clean up the merge workspace and release the lock, even on errors.
- Never touch a worktree with an active `claude` process.
- If a conflict is too complex, skip rather than guess.
