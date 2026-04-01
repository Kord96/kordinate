# Cleanup

Level 3 resource for the merge skill.

Run after merging. Also handles branches that were empty (no changes beyond main) or already merged by other means.

## For each merged or empty session branch

Skip branches that are **active** (running claude process) or **conflicted** (skipped during merge).

### Remove worktree

```bash
git worktree remove <path>
```

If the worktree directory no longer exists, this is a no-op — `git worktree prune` already handled it.

### Delete local branch

```bash
git branch -D session/<name>
```

### Final prune

```bash
git worktree prune
```

If the session branch was pushed to remote (by the worktree-push hook), delete it there too: `git push origin --delete session/<name>` after the local branch is deleted.

## For each merged or empty memory branch (`--memory`)

Skip branches that are **active** (Beorn agent still running) or **conflicted** (skipped during merge).

### Remove worktree

```bash
git -C "$KORDINATE_HOME" worktree remove <path>
```

### Delete local branch

```bash
git -C "$KORDINATE_HOME" branch -D memory/<name>
```

### Final prune

```bash
git -C "$KORDINATE_HOME" worktree prune
```

Memory branches are PVC-local — no remote branches or PRs.

## What gets cleaned up

| State | Worktree | Local branch |
|-------|----------|-------------|
| Merged | removed | deleted |
| Empty | removed | deleted |
| Active | untouched | untouched |
| Conflicted | untouched | untouched |
