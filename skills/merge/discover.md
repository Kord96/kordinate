# Discover & Classify

Level 3 resource for the merge skill.

## Session Branch Discovery (default)

```bash
git worktree prune
git branch --list 'session/*'
```

If `$ARGUMENTS` specifies a branch, filter to just that one.

Session branches may exist on remote (pushed by worktrees), but they are intermediate — the worktree-push hook merges them to main automatically.

## Kord Branch Discovery (automatic)

Kord branches in `$KORDINATE_HOME` use the `kord/` prefix (e.g., `kord/w1-kordinate`). They are discovered automatically when merging the corresponding `session/` branch — no flag needed.

```bash
git -C "$KORDINATE_HOME" worktree prune
git -C "$KORDINATE_HOME" branch --list 'kord/*'
```

## Memory Branch Discovery (`--memory`)

When the `--memory` flag is passed, discover `memory/*` branches in `$KORDINATE_HOME`:

```bash
git -C "$KORDINATE_HOME" worktree prune
git -C "$KORDINATE_HOME" branch --list 'memory/*'
```

If `$ARGUMENTS` specifies a branch, filter to just that one.

## Classify each branch

For each `session/*`, `kord/*`, or `memory/*` branch, determine its state:

### Active

A `claude` process is running in its worktree:

```bash
wt_path=$(git worktree list --porcelain | grep -B1 "branch refs/heads/$branch" | head -1 | sed 's/^worktree //')
pgrep -f "$wt_path" >/dev/null 2>&1
```

For memory branches, use `git -C "$KORDINATE_HOME" worktree list --porcelain` instead.

If active → **skip** (don't touch running sessions/agents).

### Has changes

Commits exist beyond main:

```bash
git log main..$branch --oneline
```

For memory branches: `git -C "$KORDINATE_HOME" log main..$branch --oneline`.

Non-empty → proceed to [merge-branches.md](merge-branches.md).

### Empty

No changes beyond main → skip to [cleanup.md](cleanup.md).
