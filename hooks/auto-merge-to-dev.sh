#!/bin/bash
# PostToolUse hook: after a successful git push to a session/* branch,
# ensure a PR exists, then signal Claude to run /deployer:merge-to-dev.

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

# Extract branch name from push command
BRANCH=$(echo "$PUSH_CMD" | grep -oE 'session/[^ ]+')
if [ -z "$BRANCH" ]; then
  BRANCH=$(git branch --show-current 2>/dev/null)
fi

# Create PR if one doesn't exist (async — don't block tool completion)
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

# Signal to Claude that merge-to-dev should be triggered
echo "{\"hookSpecificOutput\":{\"message\":\"REQUIRED ACTION: Push to session branch detected (${BRANCH}). PR ensured. You MUST now spawn the deployer agent to run merge-to-dev. Read ~/.claude/agents/deployer/memory.md — check ## Identity for agent_id. If one exists, use it as the resume parameter; otherwise omit resume to start fresh. Do not continue with other work until this is done.\"}}"
exit 0
