# merge

Merge session branches into main when direct fast-forward fails.

## Arguments

`\$ARGUMENTS` — Optional: specific branch name (e.g., `session/w1-logbd`). Defaults to processing all open session/* PRs.

## Context

This skill is invoked when the `auto-merge-to-dev` hook detects that a direct fast-forward push to main failed (due to conflicts or diverged history). Most pushes succeed via the hook’s fast path — this skill handles the rest.

Branch model: `main` (active development) ‒ `test` (staging) ‒ `prod` (production).

Since the caller may be inside a worktree, all operations use a temporary detached-HEAD worktree and `git push origin HEAD:main`.

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
      - `git -C /tmp/merge-workspace checkout origin/<branch> --detach`
      - `git -C /tmp/merge-workspace rebase origin/main`

   b. **If rebase succeeds**:
      - Push to main: `git -C /tmp/merge-workspace push origin HEAD:main` (fast-forward only — fails if not FF)
      - Close the PR: `gh pr close <number>`

   c. **If rebase has conflicts**:
      - Attempt to resolve by reading both sides and preserving both changes where possible
      - If too complex, skip and report: "conflict in <branch> — manual resolution needed""
      - `git -C /tmp/merge-workspace rebase --abort` if skipping

   d. **Update workspace** after each merge so subsequent rebases are against fresh main:
      - `git -C /tmp/merge-workspace checkout origin/main --detach` (main ref updated by the push in step 4b — no re-fetch needed)

5. **Cleanup**: Always runs, even on errors.
   - `git worktree remove /tmp/merge-workspace --force`
   - `rmdir .merge-lock`
   - `git worktree prune`

6. **Report results** to caller:
   - Which branches were merged (commit hashes)
   - Which branches had conflicts (and what files)
   - Current main HEAD after all merges

## Rules

- Never force-push to main — `git push origin HEAD:main` only succeeds on fast-forward.
- Use `--force-with-lease` (not `--force`) when pushing rebased session branches.
- Always use detached HEAD in the merge workspace — never checkout named branches.
- Always clean up the merge workspace and release the lock, even on errors.
- If a conflict is too complex, skip rather than guess.
