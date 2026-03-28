#!/bin/bash
# kord-gate.sh — PreToolUse hook on Agent tool.
# Blocks direct spawning of kordinate agents — redirects to /kord.
# Built-in agent types (Explore, Plan, etc.) pass through.

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

# Allow if the prompt contains the lifecycle wrapper (spawned by /kord)
PROMPT=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('tool_input', {}).get('prompt', ''))
" 2>/dev/null)
if echo "$PROMPT" | grep -q "Follow this checklist exactly. Create tasks for each item using TaskCreate"; then
  echo '{}'; exit 0
fi

# Only block if this is a kordinate agent (has a directory in agents/)
if [ -d "$KORDINATE_HOME/agents/$AGENT" ] && [ "$AGENT" != "main" ]; then
  cat <<EOF
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Use beorn capability tools (e.g., write_memory, analyze_architecture) or the delegate MCP tool instead of spawning directly."}}
EOF
  exit 0
fi

# Built-in or unknown agent type — allow
echo '{}'
exit 0
