#!/bin/bash
# auto-merge — keep session branch and main in sync on every push.
#
# Registered as PostToolUse on Bash. Triggers on git push
# from a worktree on a session/* branch.
#
# On push:
# 1. Fetch latest main from origin
# 2. Merge origin/main into the session branch (picks up other sessions' work)
# 3. Push session branch (already done by the user's command)
# 4. Fast-forward main to match session (since session now includes main)
# 5. Push main to origin
#
# If merge conflicts: don't block, suggest /merge.

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

# Skip if already pushing to main explicitly
echo "$CMD" | grep -qE 'HEAD:.*main\b' && exit 0

# Skip if HEAD is a wip commit (session exit auto-commit — not ready for main)
HEAD_MSG=$(git -C "$REPO_ROOT" log -1 --format="%s" 2>/dev/null)
if echo "$HEAD_MSG" | grep -qi "^wip"; then
  log "skipping main sync — HEAD is a wip commit"
  exit 0
fi

# Step 1: Fetch latest main
git -C "$REPO_ROOT" fetch origin main 2>/dev/null || log "fetch origin main failed"

# Step 2: Merge origin/main into session branch (picks up other sessions' work)
MERGE_OUTPUT=$(git -C "$REPO_ROOT" merge origin/main --no-edit 2>&1)
MERGE_RC=$?

if [ $MERGE_RC -ne 0 ]; then
  git -C "$REPO_ROOT" merge --abort 2>/dev/null
  log "merge origin/main into $BRANCH failed: $MERGE_OUTPUT"
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"CONFLICT: %s has diverged from main. Run /merge to resolve."}}\n' "$BRANCH"
  exit 0
fi

# Step 3: Push session branch (with the merge commit if any)
# The user's push already happened, but if we merged, we need to push again
if echo "$MERGE_OUTPUT" | grep -q "Already up to date"; then
  log "session already includes main"
else
  log "merged origin/main into $BRANCH"
  git -C "$REPO_ROOT" push origin "$BRANCH" 2>/dev/null || true
fi

# Step 4+5: Update main to match session and push
CURRENT_SHA=$(git -C "$REPO_ROOT" rev-parse HEAD)
PUSH_OUTPUT=$(git -C "$REPO_ROOT" push origin "$CURRENT_SHA:refs/heads/main" 2>&1)
PUSH_RC=$?

if [ $PUSH_RC -eq 0 ]; then
  log "main synced to $BRANCH"
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Synced %s → main."}}\n' "$BRANCH"
else
  log "push to main failed (rc=$PUSH_RC): $PUSH_OUTPUT"
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Push to main failed — may need rebase. Run /merge to resolve."}}\n' "$BRANCH"
fi
