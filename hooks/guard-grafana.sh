#!/bin/bash
# Guard hook: blocks Grafana-related operations unless sauron auth token is present.
# Covers: Grafana MCP tools, dashboard JSON edits, Grafana API/renderer calls.

INPUT=$(cat)

SECRET=$(cat "$HOME/.claude/profile/secrets/sauron" 2>/dev/null)
AUTH=$(cat /tmp/.sauron-auth 2>/dev/null)

DENY='{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Blocked: Grafana/dashboard access is restricted to the sauron agent. Spawn sauron for dashboard edits, Grafana API calls, and renderer usage."}}'

# If sauron auth token matches, allow
if [[ -n "$SECRET" && "$AUTH" == "$SECRET" ]]; then
  echo '{}'
  exit 0
fi

# Check if this is a dashboard JSON file edit (Edit or Write tool)
FILE_PATH=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)
if [[ "$FILE_PATH" == *"dashboards/"*".json" ]] || [[ "$FILE_PATH" == *"dashboard"*".json" ]]; then
  echo "$DENY"
  exit 0
fi

# Check if this is a Bash command hitting Grafana
COMMAND=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null)
if echo "$COMMAND" | grep -qi "grafana.*render\|grafana.*api/\|/render/d/\|grafana_admin\|grafana.*datasource"; then
  echo "$DENY"
  exit 0
fi

# Not grafana-related, allow
echo '{}'
exit 0
