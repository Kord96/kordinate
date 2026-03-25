#!/bin/bash
# Guard: memory and kord writes go through scribe (unless non-curated + non-templated)
# Registered in settings.json as PreToolUse hook on Write|Edit
# Exit 0 = allow, Exit 2 = block with feedback
#
# settings.json reference:
#   "command": "$KORDINATE_HOME/agents/scribe/skills/remember/guard.sh"

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

[ -z "$FILE_PATH" ] && exit 0

# Check if path matches memory or kord patterns
case "$FILE_PATH" in
  */.kord/*)
    # Allow if scribe auth token exists
    if [ -f "/tmp/.scribe-auth" ]; then
      exit 0
    fi

    # Check KORD.json — allow non-curated, non-templated files
    KORD_JSON="${KORDINATE_HOME:-$HOME/.kord}/KORD.json"
    if [ -f "$KORD_JSON" ]; then
      ENTRY=$(jq -r --arg p "$FILE_PATH" '.[] | select(.path == $p or ($p | endswith(.path)))' "$KORD_JSON" 2>/dev/null)
      if [ -n "$ENTRY" ]; then
        CURATED=$(echo "$ENTRY" | jq -r '.curated // false')
        TEMPLATE=$(echo "$ENTRY" | jq -r '.template // "none"')
        if [ "$CURATED" = "false" ] && [ "$TEMPLATE" = "none" ]; then
          exit 0  # non-curated, non-templated — allow
        fi
      fi
    fi

    echo "This file is managed by kordinate. Use /kord remember to write memories." >&2
    exit 2
    ;;
  *)
    exit 0
    ;;
esac
