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

### Delete remote branch

```bash
git push origin --delete session/<name>
```

### Close PR

If a PR exists for this branch:

```bash
gh pr close <number>
```

For merged branches, the PR was already superseded by the rebase+push to main.

### Final prune

```bash
git worktree prune
```

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

### No remote push

Memory branches live on the PVC-local repo. There is no GitHub remote — do not attempt `git push origin --delete`.

### No PR to close

Memory branches do not have PRs.

### Final prune

```bash
git -C "$KORDINATE_HOME" worktree prune
```

## What gets cleaned up

### Session branches

| State | Worktree | Local branch | Remote branch | PR |
|-------|----------|-------------|---------------|-----|
| Merged | removed | deleted | deleted | closed |
| Empty | removed | deleted | deleted | n/a |
| Active | untouched | untouched | untouched | untouched |
| Conflicted | untouched | untouched | untouched | untouched |

### Memory branches

| State | Worktree | Local branch | Remote branch | PR |
|-------|----------|-------------|---------------|-----|
| Merged | removed | deleted | n/a | n/a |
| Empty | removed | deleted | n/a | n/a |
| Active | untouched | untouched | n/a | n/a |
| Conflicted | untouched | untouched | n/a | n/a |
