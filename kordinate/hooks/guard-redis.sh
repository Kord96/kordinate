#!/bin/bash
# Guard hook: blocks Redis MCP tool calls unless deployer auth token is present.

INPUT=$(cat)

SECRET=$(cat "$HOME/.claude/profile/locks/deployer" 2>/dev/null)
AUTH=$(cat /tmp/.deployer-auth 2>/dev/null)

if [[ -n "$SECRET" && "$AUTH" == "$SECRET" ]]; then
  echo '{}'
  exit 0
else
  echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Blocked: Redis MCP access is restricted to the deployer agent. Use /consult deployer for Redis state and data queries."}}'
  exit 0
fi
