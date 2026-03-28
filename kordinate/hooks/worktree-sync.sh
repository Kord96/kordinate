#!/bin/bash
# worktree-sync — after a git commit in a worktree, rebase onto latest main.
#
# Registered as PostToolUse on Bash. When a git commit succeeds from a worktree
# on a session/* branch, this hook rebases the branch onto origin/main so
# divergence never exceeds one commit.
#
# If the rebase conflicts, aborts and warns. Does not block work.

set -uo pipefail

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
[ -n "$CMD" ] || exit 0

# Only act on git commit commands (not amend-only or other git subcommands)
echo "$CMD" | grep -qE 'git\s+((-C\s+\S+\s+)?commit|commit)' || exit 0
# Skip if this was a merge commit (avoid rebasing the merge we just did)
echo "$CMD" | grep -qE 'Merge|merge' && exit 0

# Determine repo root
GIT_C_DIR=$(echo "$CMD" | grep -oE 'git\s+-C\s+(\S+)' | awk '{print $NF}')
GIT_C_DIR="${GIT_C_DIR/#\~/$HOME}"
CD_DIR=$(echo "$CMD" | grep -oE '^\s*cd\s+(\S+)' | awk '{print $NF}')
CD_DIR="${CD_DIR/#\~/$HOME}"

if [ -n "$GIT_C_DIR" ]; then
  REPO_ROOT=$(git -C "$GIT_C_DIR" rev-parse --show-toplevel 2>/dev/null)
elif [ -n "$CD_DIR" ]; then
  REPO_ROOT=$(git -C "$CD_DIR" rev-parse --show-toplevel 2>/dev/null)
else
  REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
fi
[ -n "$REPO_ROOT" ] || exit 0

# Check if we're in a worktree (not the main repo)
COMMON_DIR=$(git -C "$REPO_ROOT" rev-parse --git-common-dir 2>/dev/null)
GIT_DIR=$(git -C "$REPO_ROOT" rev-parse --git-dir 2>/dev/null)
[ "$COMMON_DIR" != "$GIT_DIR" ] || exit 0

# Check we're on a session/* branch
BRANCH=$(git -C "$REPO_ROOT" branch --show-current 2>/dev/null)
case "$BRANCH" in
  session/*) ;;
  *) exit 0 ;;
esac

# Fetch latest main
git -C "$REPO_ROOT" fetch origin main 2>/dev/null || exit 0

# Check if we're already up to date
if git -C "$REPO_ROOT" merge-base --is-ancestor origin/main HEAD 2>/dev/null; then
  exit 0
fi

# Rebase onto main
if git -C "$REPO_ROOT" rebase origin/main 2>/dev/null; then
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Synced %s — rebased onto latest main."}}\n' "$BRANCH"
else
  git -C "$REPO_ROOT" rebase --abort 2>/dev/null
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"SYNC WARNING: %s has diverged from main and auto-rebase failed. Run /merge to resolve before divergence grows."}}\n' "$BRANCH"
fi
