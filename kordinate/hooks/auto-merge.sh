#!/bin/bash
# auto-merge — after git commit or push from a worktree, merge to main.
#
# Registered as PostToolUse on Bash. Triggers on git commit or git push
# from a worktree on a session/* branch.
#
# On success: merge locally, push to remote only on git push.
# On conflict: don't block, nudge "run /merge to resolve."

set -uo pipefail

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
[ -n "$CMD" ] || exit 0

# Only act on git commit or git push
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

# Must be a worktree (not main repo) on a session/* branch
COMMON_DIR=$(git -C "$REPO_ROOT" rev-parse --git-common-dir 2>/dev/null)
GIT_DIR=$(git -C "$REPO_ROOT" rev-parse --git-dir 2>/dev/null)
[ "$COMMON_DIR" != "$GIT_DIR" ] || exit 0

BRANCH=$(git -C "$REPO_ROOT" branch --show-current 2>/dev/null)
case "$BRANCH" in session/*) ;; *) exit 0 ;; esac

# Find the main repo root
MAIN_REPO=$(git -C "$REPO_ROOT" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
MAIN_REPO="${MAIN_REPO%/.git}"
[ -d "$MAIN_REPO/.git" ] || exit 0

# --- Merge session into main ---

# Prevent concurrent merges
mkdir "$MAIN_REPO/.merge-lock" 2>/dev/null || exit 0

WORKSPACE=$(mktemp -d)
cleanup() {
  git -C "$MAIN_REPO" worktree remove "$WORKSPACE" --force 2>/dev/null
  rmdir "$MAIN_REPO/.merge-lock" 2>/dev/null
}
trap cleanup EXIT

CURRENT_SHA=$(git -C "$REPO_ROOT" rev-parse HEAD)
git -C "$MAIN_REPO" fetch origin main 2>/dev/null || true
git -C "$MAIN_REPO" worktree add "$WORKSPACE" main 2>/dev/null || exit 0

if git -C "$WORKSPACE" merge "$CURRENT_SHA" --no-edit 2>/dev/null; then
  # Merge succeeded (fast-forward or auto-merge)
  IS_PUSH=$(echo "$CMD" | grep -qE 'git\s+((-C\s+\S+\s+)?push|push)' && echo "yes" || echo "no")

  if [ "$IS_PUSH" = "yes" ]; then
    if git -C "$WORKSPACE" push origin main 2>&1; then
      printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main and pushed."}}\n' "$BRANCH"
    else
      printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main locally. Push failed — will retry."}}\n' "$BRANCH"
    fi
  else
    printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main locally. Push on next git push."}}\n' "$BRANCH"
  fi
else
  git -C "$WORKSPACE" merge --abort 2>/dev/null
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"CONFLICT: %s has diverged from main. Run /merge to resolve."}}\n' "$BRANCH"
fi
