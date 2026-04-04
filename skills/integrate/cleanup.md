# Cleanup

Level 3 resource for the integrate skill.

Run after successful integration. Also handles branches that were empty (no changes beyond main) or already integrated by other means.

## For each integrated or empty session branch

Skip branches that are **active** (running claude process) or **conflicted** (skipped during integration).

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

Remote session branches may remain if they were published; delete them only when the operator explicitly wants remote cleanup.

## For each integrated or empty memory branch (`--memory`)

Skip branches that are **active** (agent still running) or **conflicted** (skipped during integration).

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

## What gets cleaned up

| State | Worktree | Local branch |
|-------|----------|-------------|
| Integrated | removed | deleted |
| Empty | removed | deleted |
| Active | untouched | untouched |
| Conflicted | untouched | untouched |