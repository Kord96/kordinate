---
name: merge
description: Merge session or memory branches into main, resolve conflicts, and clean up stale worktrees. Use when the worktree-push hook reports a conflict, when branches need manual merging, or to garbage-collect old worktrees.
argument-hint: "[--memory] [<branch>]"
curated: true
scope: global
---

Merge session or memory branches into main and clean up stale worktrees.

Most worktree pushes merge to main automatically via the `worktree-push` PostToolUse hook. This skill is the fallback when that hook hits conflicts, and also handles batch merging and cleanup.

`$ARGUMENTS` — Optional flags and branch names:
- `--memory` — merge `memory/*` branches in `$KORDINATE_HOME` instead of `session/*` branches in the current repo.
- Specific branch name (e.g., `session/w1-logbd` or `memory/agent-abc123`).
- Default (no flag): all session branches in current repo.

## Procedure

1. **Discover + classify** — see [discover.md](discover.md).
2. **Merge** branches with changes — see [merge-branches.md](merge-branches.md).
3. **Merge kord branches** — for each merged session branch, check if a matching `session/*` branch exists in `$KORDINATE_HOME`. If so, merge it using the memory branch procedure in [merge-branches.md](merge-branches.md). This is automatic — no `--memory` flag needed.
4. **Cleanup** merged, empty, and stale branches — see [cleanup.md](cleanup.md). Also clean up the corresponding kord branches.
5. **Report**: merged (commits), conflicted (files), cleaned up (empty), skipped (active). Include kord merge results.

## Rules

- Never force-push to main — `git push origin HEAD:main` only succeeds on fast-forward.
- Always use detached HEAD in the merge workspace — never checkout named branches.
- Always clean up the merge workspace and release the lock, even on errors.
- Never touch a worktree with an active `claude` process.
- If a conflict is too complex, skip rather than guess.
