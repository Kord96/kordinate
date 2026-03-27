#!/bin/bash
# worktree-push — after a successful git push from a worktree, merge to main.
#
# Registered as PostToolUse on Bash. When a git push succeeds from a worktree
# on a session/* branch, this hook merges the session branch into main and
# pushes main. The hook runs synchronously, blocking the agent until done.
#
# If the merge conflicts, outputs a context message suggesting /merge.

set -uo pipefail

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
[ -n "$CMD" ] || exit 0

# Only act on git push commands
echo "$CMD" | grep -qE 'git\s+((-C\s+\S+\s+)?push|push)' || exit 0

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

# --- Merge session branch into main and push ---

git -C "$MAIN_REPO" fetch origin main 2>/dev/null || true
CURRENT_SHA=$(git -C "$REPO_ROOT" rev-parse HEAD)

# Fast-forward path
if git -C "$MAIN_REPO" merge-base --is-ancestor origin/main "$CURRENT_SHA" 2>/dev/null; then
  git -C "$MAIN_REPO" update-ref refs/heads/main "$CURRENT_SHA"
  if git -C "$MAIN_REPO" push origin main 2>&1; then
    printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main and pushed (fast-forward)."}}\n' "$BRANCH"
  else
    printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main locally but push failed. Will retry on next push."}}\n' "$BRANCH"
  fi
  exit 0
fi

# Rebase path — use temp workspace
WORKSPACE=$(mktemp -d)
cleanup() {
  git -C "$MAIN_REPO" worktree remove "$WORKSPACE" --force 2>/dev/null
  rmdir "$MAIN_REPO/.merge-lock" 2>/dev/null
}
trap cleanup EXIT

mkdir "$MAIN_REPO/.merge-lock" 2>/dev/null || {
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Another merge is running. Session branch pushed but not yet on main. Will merge on next push or via /merge."}}\n'
  exit 0
}

git -C "$MAIN_REPO" worktree add "$WORKSPACE" origin/main --detach 2>/dev/null
git -C "$WORKSPACE" checkout "$BRANCH" --detach 2>/dev/null

if git -C "$WORKSPACE" rebase origin/main 2>/dev/null; then
  if git -C "$WORKSPACE" push origin HEAD:main 2>&1; then
    printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main and pushed (rebased onto origin/main)."}}\n' "$BRANCH"
  else
    printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Rebased %s onto main locally but push failed. Will retry on next push."}}\n' "$BRANCH"
  fi
else
  git -C "$WORKSPACE" rebase --abort 2>/dev/null
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"CONFLICT: %s has diverged from main and cannot be auto-rebased. Run /merge to resolve."}}\n' "$BRANCH"
fi
