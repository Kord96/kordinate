#!/bin/bash
# Guard hook: blocks Grafana MCP tool calls unless sauron auth token is present.

INPUT=$(cat)

SECRET=$(cat "$HOME/.claude/.sauron-secret" 2>/dev/null)
AUTH=$(cat /tmp/.sauron-auth 2>/dev/null)

if [[ -n "$SECRET" && "$AUTH" == "$SECRET" ]]; then
  echo '{}'
  exit 0
else
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Blocked: Grafana access is restricted to the sauron agent. Use /consult sauron for dashboard queries, metrics, and monitoring data."}}'
  exit 0
fi
