# merge-to-dev

Merge session branches into main (dev).

## Arguments

`$ARGUMENTS` — Optional: specific branch name (e.g., `session/20260312-140000`). Defaults to processing all open session/* PRs.

## Context

Claude sessions run in isolated worktrees on `session/*` branches. They push commits over time. This command integrates their work into main.

Branch model: `main` (active development) → `test` (staging) → `prod` (production).

PRs are auto-created by the `auto-merge-to-dev.sh` PostToolUse hook when pushing to session branches.

Since deployer runs from inside a worktree, it cannot `git checkout main` or `git checkout <session-branch>` (both are checked out in other worktrees). All operations use a temporary detached-HEAD worktree and `git push origin HEAD:main`.

## Steps

1. **Acquire lock**: `mkdir .merge-lock 2>/dev/null`
   - If it fails, another merge is running — report "merge already active" and stop.

2. **Create merge workspace**:
   - `git fetch origin` (single fetch — gets all refs including main and session branches)
   - `git worktree add /tmp/merge-workspace origin/main --detach`

3. **List session PRs**: `gh pr list --json number,title,headRefName --state open --jq '.[] | select(.headRefName | startswith("session/"))'`
   - If `$ARGUMENTS` specifies a branch, filter to just that one.

4. **For each session PR** (oldest first):

   a. **Checkout session branch (detached)** (already fetched in step 2):
      - `git -C /tmp/merge-workspace checkout origin/<branch> --detach` (refs already fetched — no per-branch fetch needed)
      - `git -C /tmp/merge-workspace rebase origin/main`

   b. **If rebase succeeds**:
      - Push to main: `git -C /tmp/merge-workspace push origin HEAD:main` (fast-forward only — fails if not FF)
      - Close the PR: `gh pr close <number>`

   c. **If rebase has conflicts**:
      - Attempt to resolve by reading both sides and preserving both changes where possible
      - If the session branch owner is identifiable, consult via `/agent:consult` for guidance
      - If too complex, skip and report: "conflict in <branch> — manual resolution needed"
      - `git -C /tmp/merge-workspace rebase --abort` if skipping

   d. **Update workspace** after each merge so subsequent rebases are against fresh main:
      - `git -C /tmp/merge-workspace checkout origin/main --detach` (main ref updated by the push in step 4b — no re-fetch needed)

   e. **Periodic branch cleanup** (once per day, after all PRs are processed):
      - Read `.claude/agent-state/deployer.json` for `last_branch_cleanup` date
      - If missing or older than 24 hours:
        1. List all remote `session/*` branches: `git branch -r --list 'origin/session/*'`
        2. For each, check if an active worktree exists: `git worktree list | grep <branch>`
        3. If no worktree: `git push origin --delete <branch>`
        4. If worktree exists: leave it — the session is still running
        5. Update `last_branch_cleanup` in `.claude/agent-state/deployer.json` directly via Bash
      - If less than 24 hours: skip cleanup

5. **Cleanup**: Always runs, even on errors.
   - `git worktree remove /tmp/merge-workspace --force`
   - `rmdir .merge-lock`
   - `git worktree prune`

6. **Report results** to caller:
   - Which branches were merged (commit hashes)
   - Which branches had conflicts (and what files)
   - Current main HEAD after all merges

The caller (session Claude) uses this report to rebase their worktree onto updated main.

## Rules

- Never force-push to main — `git push origin HEAD:main` only succeeds on fast-forward.
- Use `--force-with-lease` (not `--force`) when pushing rebased session branches.
- Always use detached HEAD in the merge workspace — never checkout named branches.
- Always clean up the merge workspace and release the lock, even on errors.
- Stale branch cleanup runs at most once per day (checked via `last_branch_cleanup` in `.claude/agent-state/deployer.json`). Delete remote session branches only if no active worktree exists (`git worktree list`).
- If a conflict is too complex, skip rather than guess.
