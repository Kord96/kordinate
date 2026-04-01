#!/bin/bash
# kord-gate.sh — PreToolUse hook on Agent tool.
# Blocks direct spawning of kordinate agents unless authorized by kord.
# Built-in agent types (Explore, Plan, etc.) pass through.
#
# Authorization: kord MCP returns a one-time gate secret. The caller
# writes it to /tmp/.kord-gate-<agent>. This hook checks and consumes it.

INPUT=$(cat)

AGENT=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
name = d.get('tool_input', {}).get('subagent_type', '')
print(name.lower())
" 2>/dev/null)

# No agent type or empty — allow
[ -z "$AGENT" ] && { echo '{}'; exit 0; }

KORDINATE_HOME="${KORDINATE_HOME:-$HOME/.kord}"

# Only gate kordinate agents (has a directory in agents/)
if [ -d "$KORDINATE_HOME/agents/$AGENT" ] && [ "$AGENT" != "main" ]; then

  # Check for kord gate secret — one-time use, consumed on check
  GATE_FILE="/tmp/.kord-gate-${AGENT}"
  LOCK_FILE="$KORDINATE_HOME/profile/locks/${AGENT}"
  if [ -f "$GATE_FILE" ] && [ -f "$LOCK_FILE" ]; then
    if [ "$(cat "$GATE_FILE")" = "$(cat "$LOCK_FILE")" ]; then
      rm -f "$GATE_FILE"
      echo '{}'; exit 0
    fi
  fi

  cat <<EOF
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Use kord MCP tools (e.g., mcp__kord__delegate, mcp__kord__write_memory) to interact with agents. Kord will authorize local spawning when appropriate."}}
EOF
  exit 0
fi

# Built-in or unknown agent type — allow
echo '{}'
exit 0
