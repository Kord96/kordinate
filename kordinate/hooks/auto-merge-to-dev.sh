#!/bin/bash
# PostToolUse hook: after a successful git push to a session/* branch,
# try a direct fast-forward push to main. If it fails, signal to use /merge.

INPUT=$(cat)

# Fast exit: if input doesn't contain both "git push" and "session/", nothing to do
case "$INPUT" in
  *git\ push*session/*) ;;
  *session/*git\ push*) ;;
  *) echo '{}'; exit 0 ;;
esac

# Extract command from tool_input
CMD=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)

# Check if the command was a git push to a session branch
PUSH_CMD=$(echo "$CMD" | grep -oE 'git\s+push[^&;]*' | head -1)
if [ -z "$PUSH_CMD" ]; then
  echo '{}'
  exit 0
fi

if ! echo "$PUSH_CMD" | grep -qE 'session/'; then
  echo '{}'
  exit 0
fi

# Extract branch name
BRANCH=$(echo "$PUSH_CMD" | grep -oE 'session/[^ ]+')
if [ -z "$BRANCH" ]; then
  BRANCH=$(git branch --show-current 2>/dev/null)
fi

# Create PR if one doesn't exist (async)
(
  EXISTING_PR=$(gh pr list --head "$BRANCH" --json number --jq '.[0].number' 2>/dev/null)
  if [ -z "$EXISTING_PR" ]; then
    SESSION_ID="${BRANCH##session/}"
    gh pr create \
      --title "session: ${SESSION_ID}" \
      --body "Auto-created from Claude session worktree." \
      --base main \
      --head "$BRANCH" 2>/dev/null
  fi
) &

# Try direct fast-forward push to main
git fetch origin main 2>/dev/null
if git merge-base --is-ancestor origin/main HEAD 2>/dev/null; then
  # HEAD is ahead of origin/main — FF is possible
  if git push origin HEAD:main 2>/dev/null; then
    echo "{\"hookSpecificOutput\":{\"message\":\"Session branch ${BRANCH} merged to main (fast-forward). PR will be closed automatically.\"}}"
    # Close PR async
    (gh pr close "$BRANCH" 2>/dev/null) &
    exit 0
  fi
fi

# FF push failed — tell agent to use merge skill
echo "{\"hookSpecificOutput\":{\"message\":\"Push to session branch ${BRANCH} succeeded, but fast-forward to main failed (likely conflicts). Run /merge to rebase and resolve.\"}}"
exit 0
