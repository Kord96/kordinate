---
name: session
description: Inspect and manage worktree-backed Claude sessions. List active worktrees, show sync state, and print commands to resume or create sessions.
argument-hint: "[list|current|new <name>|resume <selector>|inspect|prune]"
curated: true
scope: global
---

Inspect and manage worktree-backed Claude sessions.

`$ARGUMENTS` controls the mode:
- `list` (default) — list current session worktrees and their sync state
- `current` — show the current repo/worktree/branch and sync state
- `new <name>` — print the command to start or create a named worktree session
- `resume <selector>` — print the command to resume an existing worktree by slug, branch, or path
- `inspect` — print the command to run Claude in the current tree without selecting/creating a worktree
- `prune` — prune stale worktree metadata and show the remaining session worktrees

## Rules

- This skill is informational/control-plane only. It does not mutate git state directly.
- Use `git fetch --all --prune` before reporting sync state.
- When inside a worktree, treat it as the active session and show it explicitly.
- Prefer printing the exact `claude-session` command the user should run rather than switching tmux state implicitly.

## Procedure

Use the helper backend:

```bash
bin/session-status $ARGUMENTS
```

Behavior by mode:
- `list` — enumerate `session/*` worktrees and report worktree/path, branch, dirty/clean, ahead/behind, and drift from `main`
- `current` — report the same fields for the current tree
- `new` — print `claude-session --new-worktree <name>`
- `resume` — print `claude-session --select-worktree <selector>`
- `inspect` — print `claude-session --inspect-current-tree`

The helper may fetch safely before reporting sync state, but it must not mutate branches.

## Output

Keep output concise and operational. Always include the exact next command for non-list modes.