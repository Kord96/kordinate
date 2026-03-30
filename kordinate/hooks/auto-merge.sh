#!/bin/bash
# auto-merge — after git commit or push from a worktree, merge to main.
#
# Registered as PostToolUse on Bash. Triggers on git commit or git push
# from a worktree on a session/* branch.
#
# On success: merge locally, push to remote only on git push.
# On conflict: don't block, nudge "run /merge to resolve."

set -uo pipefail

log() { echo "[auto-merge] $*" >&2; }

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
if [ -z "$REPO_ROOT" ]; then
  log "could not determine repo root, skipping"
  exit 0
fi

# Must be a worktree (not main repo) on a session/* branch
COMMON_DIR=$(git -C "$REPO_ROOT" rev-parse --git-common-dir 2>/dev/null)
GIT_DIR=$(git -C "$REPO_ROOT" rev-parse --git-dir 2>/dev/null)
if [ "$COMMON_DIR" = "$GIT_DIR" ]; then
  log "not a worktree, skipping"
  exit 0
fi

BRANCH=$(git -C "$REPO_ROOT" branch --show-current 2>/dev/null)
case "$BRANCH" in session/*) ;; *) exit 0 ;; esac

# Find the main repo root
MAIN_REPO=$(git -C "$REPO_ROOT" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
MAIN_REPO="${MAIN_REPO%/.git}"
if [ ! -d "$MAIN_REPO/.git" ]; then
  log "main repo not found at $MAIN_REPO, skipping"
  exit 0
fi

# --- Merge session into main ---

# Prevent concurrent merges
if ! mkdir "$MAIN_REPO/.merge-lock" 2>/dev/null; then
  log "merge lock held, skipping"
  exit 0
fi

WORKSPACE=$(mktemp -d)
cleanup() {
  if [ "$USED_EXISTING_WORKTREE" = false ]; then
    git -C "$MAIN_REPO" worktree remove "$WORKSPACE" --force 2>/dev/null
  fi
  rmdir "$MAIN_REPO/.merge-lock" 2>/dev/null
}
trap cleanup EXIT

CURRENT_SHA=$(git -C "$REPO_ROOT" rev-parse HEAD)
git -C "$MAIN_REPO" fetch origin main 2>/dev/null || log "fetch origin main failed, continuing with local"

USED_EXISTING_WORKTREE=false
if ! git -C "$MAIN_REPO" worktree add "$WORKSPACE" main 2>/dev/null; then
  # main may already be checked out in another worktree — find it
  EXISTING_WT=$(git -C "$MAIN_REPO" worktree list --porcelain 2>/dev/null \
    | awk '/^worktree /{wt=$2} /^branch refs\/heads\/main$/{print wt}')
  if [ -n "$EXISTING_WT" ]; then
    log "main already checked out at $EXISTING_WT, using it"
    WORKSPACE="$EXISTING_WT"
    USED_EXISTING_WORKTREE=true
  else
    log "failed to create merge worktree for main"
    exit 0
  fi
fi

if git -C "$WORKSPACE" merge "$CURRENT_SHA" --no-edit 2>/dev/null; then
  # Merge succeeded — but check for structural conflicts (renames undone by directory moves)
  MERGE_BASE=$(git -C "$WORKSPACE" merge-base HEAD~ "$CURRENT_SHA" 2>/dev/null)
  STRUCTURAL_CONFLICT=false

  if [ -n "$MERGE_BASE" ]; then
    # Detect renames on each side since the merge base
    MAIN_RENAMES=$(git -C "$WORKSPACE" diff --diff-filter=R --name-status "$MERGE_BASE" HEAD~ 2>/dev/null | awk '{print $2 " " $3}')
    SESSION_RENAMES=$(git -C "$WORKSPACE" diff --diff-filter=R --name-status "$MERGE_BASE" "$CURRENT_SHA" 2>/dev/null | awk '{print $2 " " $3}')

    # Check if any file renamed on one side exists under the OLD name in the merge result
    if [ -n "$MAIN_RENAMES" ]; then
      while IFS=' ' read -r old_name new_name; do
        if [ -n "$old_name" ] && git -C "$WORKSPACE" ls-files --error-unmatch "$old_name" >/dev/null 2>&1; then
          log "structural conflict: main renamed $old_name → $new_name but old name exists in merge"
          STRUCTURAL_CONFLICT=true
        fi
      done <<< "$MAIN_RENAMES"
    fi
    if [ -n "$SESSION_RENAMES" ]; then
      while IFS=' ' read -r old_name new_name; do
        if [ -n "$old_name" ] && git -C "$WORKSPACE" ls-files --error-unmatch "$old_name" >/dev/null 2>&1; then
          log "structural conflict: $BRANCH renamed $old_name → $new_name but old name exists in merge"
          STRUCTURAL_CONFLICT=true
        fi
      done <<< "$SESSION_RENAMES"
    fi
  fi

  if [ "$STRUCTURAL_CONFLICT" = true ]; then
    log "aborting merge due to structural conflicts — needs manual /merge"
    git -C "$WORKSPACE" reset --hard HEAD~ 2>/dev/null
    printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"STRUCTURAL CONFLICT: %s has file renames that collide with directory moves on main. Run /merge to resolve — auto-merge cannot safely handle this."}}\n' "$BRANCH"
    exit 0
  fi

  log "merged $BRANCH ($CURRENT_SHA) into main"
  IS_PUSH=$(echo "$CMD" | grep -qE 'git\s+((-C\s+\S+\s+)?push|push)' && echo "yes" || echo "no")

  if [ "$IS_PUSH" = "yes" ]; then
    PUSH_OUTPUT=$(git -C "$WORKSPACE" push origin main 2>&1)
    PUSH_RC=$?
    if [ $PUSH_RC -eq 0 ]; then
      log "pushed main to origin"
      printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main and pushed."}}\n' "$BRANCH"
    else
      log "push to origin failed (rc=$PUSH_RC): $PUSH_OUTPUT"
      printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main locally. Push failed — will retry."}}\n' "$BRANCH"
    fi
  else
    printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Merged %s to main locally. Push on next git push."}}\n' "$BRANCH"
  fi
else
  log "merge conflict: $BRANCH ($CURRENT_SHA) into main"
  git -C "$WORKSPACE" merge --abort 2>/dev/null
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"CONFLICT: %s has diverged from main. Run /merge to resolve."}}\n' "$BRANCH"
fi
