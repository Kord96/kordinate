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
      # Sync runtime before spawning — ensures agent reads latest files
      REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
      KORD_PKG="$REPO_ROOT/kordinate"
      if [ -d "$KORD_PKG/agents" ]; then
        for id in "$KORD_PKG"/agents/*/IDENTITY.md; do
          [ -f "$id" ] && cp "$id" "$HOME/.claude/agents/$(basename "$(dirname "$id")").md" 2>/dev/null
        done
        for a in "$KORD_PKG"/agents/*/; do
          agent=$(basename "$a")
          [ -d "$a/skills" ] && cp -r "$a/skills/"* "$KORDINATE_HOME/agents/$agent/skills/" 2>/dev/null
          for f in "$a"/memory/*.md; do
            [ -f "$f" ] && cp "$f" "$KORDINATE_HOME/agents/$agent/memory/" 2>/dev/null
          done
        done
        for s in "$KORD_PKG"/team/skills/*/; do
          skill=$(basename "$s")
          mkdir -p "$HOME/.claude/skills/$skill"
          cp "$s"*.md "$HOME/.claude/skills/$skill/" 2>/dev/null
        done
      fi
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
