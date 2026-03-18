#!/bin/bash
# Guard hook: blocks Edit/Write on .md files unless scribe auth token is present.
# Scribe places the token at /tmp/.scribe-auth before writing, removes it after.

INPUT=$(cat)

# Extract file_path from tool_input
FILE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)

# Only guard .md files (exempt agent memory directories)
if [[ "$FILE" == *.md ]] && [[ "$FILE" != */agent-memory/* ]] && [[ "$FILE" != */agents/memory/* ]]; then
  SECRET=$(cat "$HOME/.claude/profile/locks/scribe" 2>/dev/null)
  AUTH=$(cat /tmp/.scribe-auth 2>/dev/null)

  if [[ -n "$SECRET" && "$AUTH" == "$SECRET" ]]; then
    # Valid scribe auth — allow
    echo '{}'
    exit 0
  else
    # No valid auth — deny
    echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Blocked: .md files can only be written by scribe (missing auth token)."}}'
    exit 0
  fi
fi

# Not an .md file — allow
echo '{}'
exit 0
