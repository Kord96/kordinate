#!/bin/bash
# Guard hook: blocks git push to protected environment branches (test, prod).
# Pushes to main and session/* are allowed from anywhere.
# test/prod require deployer auth token.

INPUT=$(cat)

# Fast exit: if input doesn't contain "git push", nothing to guard
case "$INPUT" in
  *git\ push*|*git\ \ push*) ;;
  *) echo '{}'; exit 0 ;;
esac

# Extract command from tool_input
CMD=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)

# Commands may be chained with && or ; — isolate the git push segment
PUSH_CMD=$(echo "$CMD" | grep -oE 'git\s+push[^&;]*' | head -1)

# Only guard git push commands
if [ -z "$PUSH_CMD" ]; then
  echo '{}'
  exit 0
fi

# Determine target branch
BRANCH=$(echo "$PUSH_CMD" | grep -oE 'origin\s+(\S+)' | awk '{print $2}')
# Handle "HEAD:main" style refs
BRANCH=$(echo "$BRANCH" | sed 's/.*://')
if [ -z "$BRANCH" ]; then
  BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
fi

# Allow pushes to main and session/* from anywhere
case "$BRANCH" in
  main|session/*) echo '{}'; exit 0 ;;
esac

# For test/prod, check deployer auth
SECRET=$(cat "$HOME/.claude/.deployer-secret" 2>/dev/null)
AUTH=$(cat /tmp/.deployer-auth 2>/dev/null)

if [[ -n "$SECRET" && "$AUTH" == "$SECRET" ]]; then
  echo '{}'
  exit 0
fi

echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"Blocked: direct push to '$BRANCH' is not allowed. To roll between environments, use /deployer:roll.\"}}"
exit 0
