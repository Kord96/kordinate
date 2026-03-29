#!/bin/bash
# auto-merge — after a git commit or push from a worktree, merge to main.
#
# Registered as PostToolUse on Bash. Triggers on git commit or git push
# from a worktree on a session/* branch. Keeps drift minimal by merging
# on every commit, not just push.
#
# Strategy:
#   1. Fast-forward if possible (cheapest)
#   2. Auto-merge in temp workspace if no conflicts
#   3. If conflict → don't block, nudge: "run /merge to resolve"

set -uo pipefail

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
[ -n "$CMD" ] || exit 0

# Only act on git commit or git push commands
echo "$CMD" | grep -qE 'git\s+((-C\s+\S+\s+)?(commit|push))' || exit 0

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

# Find the main repo root
MAIN_REPO=$(git -C "$REPO_ROOT" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
MAIN_REPO="${MAIN_REPO%/.git}"
[ -d "$MAIN_REPO/.git" ] || exit 0

# --- Merge session branch into main ---

git -C "$MAIN_REPO" fetch origin main 2>/dev/null || true
CURRENT_SHA=$(git -C "$REPO_ROOT" rev-parse HEAD)

# Path 1: Fast-forward (main is ancestor of our HEAD)
if git -C "$MAIN_REPO" merge-base --is-ancestor origin/main "$CURRENT_SHA" 2>/dev/null; then
  git -C "$MAIN_REPO" update-ref refs/heads/main "$CURRENT_SHA"
  # Only push if this was a push command (don't push on every commit)
  if echo "$CMD" | grep -qE 'git\s+((-C\s+\S+\s+)?push|push)'; then
    if git -C "$MAIN_REPO" push origin main 2>&1; then
      printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main and pushed (fast-forward)."}}\n' "$BRANCH"
    else
      printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main locally. Push failed — will retry on next push."}}\n' "$BRANCH"
    fi
  else
    printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main locally (fast-forward). Push on next git push."}}\n' "$BRANCH"
  fi
  exit 0
fi

# Path 2: Auto-merge in temp workspace
# Use a lock to prevent concurrent merges
mkdir "$MAIN_REPO/.merge-lock" 2>/dev/null || {
  # Another merge running — skip silently
  exit 0
}

WORKSPACE=$(mktemp -d)
cleanup() {
  git -C "$MAIN_REPO" worktree remove "$WORKSPACE" --force 2>/dev/null
  rmdir "$MAIN_REPO/.merge-lock" 2>/dev/null
}
trap cleanup EXIT

git -C "$MAIN_REPO" worktree add "$WORKSPACE" origin/main --detach 2>/dev/null || exit 0
git -C "$WORKSPACE" merge "$CURRENT_SHA" --no-edit 2>/dev/null

if [ $? -eq 0 ]; then
  # Auto-merge succeeded
  MERGE_SHA=$(git -C "$WORKSPACE" rev-parse HEAD)
  git -C "$MAIN_REPO" update-ref refs/heads/main "$MERGE_SHA"

  if echo "$CMD" | grep -qE 'git\s+((-C\s+\S+\s+)?push|push)'; then
    if git -C "$MAIN_REPO" push origin main 2>&1; then
      printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main and pushed (auto-merge)."}}\n' "$BRANCH"
    else
      printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main locally. Push failed — will retry."}}\n' "$BRANCH"
    fi
  else
    printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main locally (auto-merge). Push on next git push."}}\n' "$BRANCH"
  fi
else
  # Conflict — don't block, nudge
  git -C "$WORKSPACE" merge --abort 2>/dev/null
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"CONFLICT: %s has diverged from main. Run /merge to resolve."}}\n' "$BRANCH"
fi
