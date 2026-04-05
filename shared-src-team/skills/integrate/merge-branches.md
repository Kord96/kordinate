# Integrate Branches

Level 3 resource for the integrate skill.

Since the caller may be inside a worktree, all operations use a temporary detached-HEAD worktree and a visible fast-forward push to `main`.

## Setup (session branches — default)

1. Acquire lock: `mkdir .integrate-lock 2>/dev/null`
   - If it fails, another integration is running — report `integration already active` and stop.
2. Fetch latest: `git fetch origin main`
3. Create integration workspace: `git worktree add /tmp/integrate-workspace origin/main --detach`

## Setup (memory branches — `--memory`)

Memory branches operate on `$KORDINATE_HOME`, not the current repo. Use `flock` for concurrent safety:

1. Acquire lock:
   ```bash
   mkdir -p "$KORDINATE_HOME/.locks"
   exec 9>"$KORDINATE_HOME/.locks/integrate.lock"
   flock -n 9 || { echo "integration already active"; exit 1; }
   ```
2. Create integration workspace:
   ```bash
   mkdir -p "$KORDINATE_HOME/.worktrees"
   git -C "$KORDINATE_HOME" worktree add "$KORDINATE_HOME/.worktrees/integrate-workspace" main --detach
   ```

## For each branch with changes (oldest first)

### Checkout + rebase

```bash
git -C $WORKSPACE checkout <branch> --detach
git -C $WORKSPACE rebase origin/main
```

Where `$WORKSPACE` is `/tmp/integrate-workspace` for session branches or `$KORDINATE_HOME/.worktrees/integrate-workspace` for memory branches.

### If rebase succeeds

Push to main (fast-forward only):

```bash
git -C $WORKSPACE push origin HEAD:main
```

For memory branches, update main locally:

```bash
git -C "$KORDINATE_HOME" update-ref refs/heads/main HEAD
```

Update workspace so subsequent rebases are against fresh main:

```bash
git -C $WORKSPACE checkout main --detach
```

### If rebase has conflicts

- Report the branch and conflict files clearly.
- Attempt resolution only when both sides can be preserved safely.
- If too complex, skip and report `conflict in <branch> — manual resolution needed`.
- `git -C $WORKSPACE rebase --abort` if skipping.

## Teardown

Always runs, even on errors.

### Session branches

```bash
git worktree remove /tmp/integrate-workspace --force
rmdir .integrate-lock
```

### Memory branches

```bash
git -C "$KORDINATE_HOME" worktree remove "$KORDINATE_HOME/.worktrees/integrate-workspace" --force
flock -u 9
```