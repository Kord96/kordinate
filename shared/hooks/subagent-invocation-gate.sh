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

WORKSTATION_HOME="${WORKSTATION_HOME:-$HOME}"
KORD_SOURCE_ROOT="${KORD_SOURCE_ROOT:-$HOME/repos/kordinate}"
KORD_LOCAL_STATE="${KORD_LOCAL_STATE:-$HOME/.local/share/kordinate}"
KORD_LOCKS_DIR="${KORD_LOCKS_DIR:-$KORD_LOCAL_STATE/locks}"

# Only gate kordinate agents (has a directory in agents/)
if [ -d "$KORD_SOURCE_ROOT/agents/$AGENT" ] && [ "$AGENT" != "main" ]; then
  mkdir -p "$KORD_LOCKS_DIR"

  # Check for kord gate secret — one-time use, consumed on check
  GATE_FILE="/tmp/.kord-gate-${AGENT}"
  LOCK_FILE="$KORD_LOCKS_DIR/${AGENT}"
  if [ -f "$GATE_FILE" ] && [ -f "$LOCK_FILE" ]; then
    if [ "$(cat "$GATE_FILE")" = "$(cat "$LOCK_FILE")" ]; then
      rm -f "$GATE_FILE"
      echo '{}'; exit 0
    fi
  fi

  cat <<EOF
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Use kord MCP tools (e.g., mcp__kord__list_agents, mcp__kord__get_agent, mcp__kord__delegate) to interact with agents. Kord will authorize local spawning when appropriate."}}
EOF
  exit 0
fi

# Built-in or unknown agent type — allow
echo '{}'
exit 0
