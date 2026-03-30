#!/bin/bash
# auto-merge — redirect all pushes from session branches to main.
#
# Registered as PostToolUse on Bash. Triggers on git push
# from a worktree on a session/* branch.
#
# Worktrees stay isolated locally (each session has its own branch).
# But on the remote, only main exists. This hook ensures every push
# goes to main, not to the session branch.
#
# If main has diverged (another session pushed first), the push fails
# and the user needs to pull --rebase and retry.

set -uo pipefail

log() { echo "[auto-merge] $*" >&2; }

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
[ -n "$CMD" ] || exit 0

# Only act on git push
echo "$CMD" | grep -qE 'git\s+((-C\s+\S+\s+)?push)' || exit 0

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
if [ -z "$REPO_ROOT" ]; then
  log "could not determine repo root, skipping"
  exit 0
fi

# Must be a worktree on a session/* branch
COMMON_DIR=$(git -C "$REPO_ROOT" rev-parse --git-common-dir 2>/dev/null)
GIT_DIR=$(git -C "$REPO_ROOT" rev-parse --git-dir 2>/dev/null)
if [ "$COMMON_DIR" = "$GIT_DIR" ]; then
  exit 0
fi

BRANCH=$(git -C "$REPO_ROOT" branch --show-current 2>/dev/null)
case "$BRANCH" in session/*) ;; *) exit 0 ;; esac

# Skip if already pushing to main
echo "$CMD" | grep -qE ':main\b|push.*main' && exit 0

# Push to main
CURRENT_SHA=$(git -C "$REPO_ROOT" rev-parse HEAD)
PUSH_OUTPUT=$(git -C "$REPO_ROOT" push origin "$CURRENT_SHA:refs/heads/main" 2>&1)
PUSH_RC=$?

if [ $PUSH_RC -eq 0 ]; then
  log "pushed $BRANCH → main"
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Pushed %s to main."}}\n' "$BRANCH"
else
  log "push to main failed (rc=$PUSH_RC): $PUSH_OUTPUT"
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Push to main failed — run: git fetch origin main && git rebase origin/main, then push again."}}\n' "$BRANCH"
fi
