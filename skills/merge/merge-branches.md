# Merge Branches

Level 3 resource for the merge skill.

Since the caller may be inside a worktree, all operations use a temporary detached-HEAD worktree and `git push origin HEAD:main`.

Branch model: `main` (active development) — `test` (staging) — `prod` (production).

## Setup (session branches — default)

1. Acquire lock: `mkdir .merge-lock 2>/dev/null`
   - If it fails, another merge is running — report "merge already active" and stop.
2. Fetch latest: `git fetch origin main`
3. Create merge workspace: `git worktree add /tmp/merge-workspace origin/main --detach`

## Setup (memory branches — `--memory`)

Memory branches operate on `$KORDINATE_HOME`, not the current repo. Multiple Beorn agents may complete simultaneously, so use `flock` for concurrent safety:

1. Acquire lock:
   ```bash
   mkdir -p "$KORDINATE_HOME/.locks"
   exec 9>"$KORDINATE_HOME/.locks/merge.lock"
   flock -n 9 || { echo "merge already active"; exit 1; }
   ```
2. Create merge workspace:
   ```bash
   mkdir -p "$KORDINATE_HOME/.worktrees"
   git -C "$KORDINATE_HOME" worktree add "$KORDINATE_HOME/.worktrees/merge-workspace" main --detach
   ```

The workspace is on the PVC (not `/tmp`) so it survives container restarts.

## For each branch with changes (oldest first)

### Checkout + rebase

```bash
git -C $WORKSPACE checkout <branch> --detach
git -C $WORKSPACE rebase origin/main
```

Where `$WORKSPACE` is `/tmp/merge-workspace` for session branches or `$KORDINATE_HOME/.worktrees/merge-workspace` for memory branches. Session branches are local — no `origin/` prefix.

### If rebase succeeds

Push to main (fast-forward only):

```bash
git -C $WORKSPACE push origin HEAD:main
```

For memory branches, this is a local push (no remote) — update main directly:

```bash
git -C "$KORDINATE_HOME" update-ref refs/heads/main HEAD
```

Update workspace so subsequent rebases are against fresh main:

```bash
git -C $WORKSPACE checkout main --detach
```

### If rebase has conflicts

- Attempt to resolve by reading both sides and preserving both changes where possible.
- **Memory branches are almost always append-only** (scratchpad appends, new topic files). For `scratchpad.md` conflicts, keep both entries — concatenate both sides' additions. New topic files should not conflict.
- If too complex, skip and report: "conflict in `<branch>` — manual resolution needed"
- `git -C $WORKSPACE rebase --abort` if skipping.

## Teardown

Always runs, even on errors.

### Session branches

```bash
git worktree remove /tmp/merge-workspace --force
rmdir .merge-lock
```

### Memory branches

```bash
git -C "$KORDINATE_HOME" worktree remove "$KORDINATE_HOME/.worktrees/merge-workspace" --force
flock -u 9
```
