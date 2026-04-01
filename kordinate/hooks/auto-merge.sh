#!/bin/bash
# auto-merge — keep session branch and target branch in sync on every push.
#
# Target branch is configurable per repo via .kord/merge-target file.
# Default: "main".
#
# On push from a session/* worktree:
# 1. Fetch latest target from origin
# 2. Merge origin/target into the session branch (picks up other sessions' work)
# 3. Push session branch again (if merge added commits)
# 4. Fast-forward target to match session
# 5. Push target to origin
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

# Determine target branch — configurable per repo
# Priority: .kord/merge-target > KORD_MERGE_TARGET env > "main"
MAIN_REPO=$(git -C "$REPO_ROOT" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
MAIN_REPO="${MAIN_REPO%/.git}"

TARGET=""
# Check repo-level config
if [ -f "$MAIN_REPO/.kord/merge-target" ]; then
  TARGET=$(cat "$MAIN_REPO/.kord/merge-target" | head -1 | tr -d '[:space:]')
fi
# Check env override
if [ -z "$TARGET" ] && [ -n "${KORD_MERGE_TARGET:-}" ]; then
  TARGET="$KORD_MERGE_TARGET"
fi
# Default: main
if [ -z "$TARGET" ]; then
  TARGET="main"
fi

log "target branch: $TARGET"

# Skip if already pushing to target explicitly
echo "$CMD" | grep -qE "HEAD:.*${TARGET}\b" && exit 0

# Skip if HEAD is a wip commit (session exit auto-commit — not ready for target)
HEAD_MSG=$(git -C "$REPO_ROOT" log -1 --format="%s" 2>/dev/null)
if echo "$HEAD_MSG" | grep -qi "^wip"; then
  log "skipping sync — HEAD is a wip commit"
  exit 0
fi

# Step 1: Fetch latest target
git -C "$REPO_ROOT" fetch origin "$TARGET" 2>/dev/null || log "fetch origin $TARGET failed"

# Step 2: Merge origin/target into session branch
MERGE_OUTPUT=$(git -C "$REPO_ROOT" merge "origin/$TARGET" --no-edit 2>&1)
MERGE_RC=$?

if [ $MERGE_RC -ne 0 ]; then
  git -C "$REPO_ROOT" merge --abort 2>/dev/null
  log "merge origin/$TARGET into $BRANCH failed: $MERGE_OUTPUT"
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"CONFLICT: %s has diverged from %s. Run /merge to resolve."}}\n' "$BRANCH" "$TARGET"
  exit 0
fi

# Step 3: Push session branch (if merge added commits)
if echo "$MERGE_OUTPUT" | grep -q "Already up to date"; then
  log "session already includes $TARGET"
else
  log "merged origin/$TARGET into $BRANCH"
  git -C "$REPO_ROOT" push origin "$BRANCH" 2>/dev/null || true
fi

# Step 4+5: Update target to match session and push
CURRENT_SHA=$(git -C "$REPO_ROOT" rev-parse HEAD)
PUSH_OUTPUT=$(git -C "$REPO_ROOT" push origin "$CURRENT_SHA:refs/heads/$TARGET" 2>&1)
PUSH_RC=$?

if [ $PUSH_RC -eq 0 ]; then
  log "$TARGET synced to $BRANCH"
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Synced %s → %s."}}\n' "$BRANCH" "$TARGET"
else
  log "push to $TARGET failed (rc=$PUSH_RC): $PUSH_OUTPUT"
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Push to %s failed — may need rebase. Run /merge to resolve."}}\n' "$TARGET"
fi
