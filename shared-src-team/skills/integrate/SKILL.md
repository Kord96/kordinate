---
name: integrate
description: Explicitly reconcile session or memory branches with main, handle conflicts visibly, and optionally clean up merged worktrees.
argument-hint: "[--memory] [<branch>]"
curated: true
scope: global
---

Explicitly reconcile session or memory branches with `main` and clean up stale worktrees when appropriate.

This is the only supported landing path to `main`.

`$ARGUMENTS` — Optional flags and branch names:
- `--memory` — integrate `memory/*` branches in `$KORDINATE_HOME` instead of `session/*` branches in the current repo.
- Specific branch name (e.g. `session/w1-logbd` or `memory/agent-abc123`).
- Default (no flag): all session branches in the current repo.

## Procedure

1. **Discover + classify** — see [discover.md](discover.md).
2. **Integrate** branches with changes — see [merge-branches.md](merge-branches.md).
3. **Cleanup** merged, empty, and stale branches — see [cleanup.md](cleanup.md). Cleanup is explicit post-success work, not hidden background behavior.
4. **Report**: integrated (commits), conflicted (files), cleaned up (empty), skipped (active).

## Rules

- Never force-push to main.
- Always fetch before integration.
- Always use a detached merge workspace — never integrate directly in a user worktree.
- Never touch a worktree with an active `claude` process.
- If a conflict is too complex, stop and report it clearly instead of guessing.
- Treat cleanup as a visible post-success step.