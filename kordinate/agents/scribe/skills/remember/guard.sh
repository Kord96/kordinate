#!/bin/bash
# Guard: memory and kord writes go through scribe
# Registered in settings.json as PostToolUse hook on Write|Edit
# Exit 0 = allow, Exit 2 = block with feedback
#
# settings.json reference:
#   "command": "$KORDINATE_HOME/agents/scribe/skills/remember/guard.sh"

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

[ -z "$FILE_PATH" ] && exit 0

# Check if path matches memory or kord patterns
case "$FILE_PATH" in
  */kord/*|*/memory/*|*/agent-memory/*)
    # Allow if scribe auth token exists
    if [ -f "/tmp/.scribe-auth" ]; then
      exit 0
    fi
    echo "Memory and kord writes go through scribe. Delegate with /scribe:remember" >&2
    exit 2
    ;;
  *)
    exit 0
    ;;
esac
