#!/bin/bash
# Guard hook: blocks git push to protected branches unless deployer auth token is present.
# Only session/* branches are pushable by non-deployer agents.

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

# Allow pushes to session/* branches
if echo "$PUSH_CMD" | grep -qE 'session/'; then
  echo '{}'
  exit 0
fi

# For any other git push, check deployer auth
SECRET=$(cat "$HOME/.claude/.deployer-secret" 2>/dev/null)
AUTH=$(cat /tmp/.deployer-auth 2>/dev/null)

if [[ -n "$SECRET" && "$AUTH" == "$SECRET" ]]; then
  echo '{}'
  exit 0
fi

BRANCH=$(echo "$PUSH_CMD" | grep -oE 'origin\s+(\S+)' | awk '{print $2}')
if [ -z "$BRANCH" ]; then
  BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
fi

echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"Blocked: direct push to '$BRANCH' is not allowed. Session agents can only push to session/* branches. To merge into main, use /deployer:merge-to-dev. To roll between environments, use /deployer:roll.\"}}"
exit 0
