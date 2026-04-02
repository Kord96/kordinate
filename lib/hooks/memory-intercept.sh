#!/bin/bash
# memory-intercept.sh — PreToolUse hook for Write|Edit
#
# If target path is under memory/, deny the write and publish to Kafka
# via the runner's /memory-update endpoint. All other writes pass through.

set -uo pipefail
INPUT=$(cat)

allow() { echo '{}'; exit 0; }
deny() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}' "$1"
  exit 0
}

# Extract file path from tool input
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null)
[ -z "$FILE_PATH" ] && allow

# Check if path is under memory/
case "$FILE_PATH" in
  */memory/*)
    # Extract the content being written
    CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // .tool_input.new_string // empty' 2>/dev/null)
    AGENT="${AGENT_NAME:-unknown}"

    # Publish to runner's memory-update endpoint (Kafka producer)
    curl -s -X POST "http://localhost:9090/memory-update" \
      -H "Content-Type: application/json" \
      -d "$(jq -n \
        --arg path "$FILE_PATH" \
        --arg content "$CONTENT" \
        --arg agent "$AGENT" \
        '{path: $path, content: $content, agent: $agent, timestamp: (now | todate)}')" \
      >/dev/null 2>&1

    deny "Memory update queued for curation. The master curator will merge your insight into the shared memory files."
    ;;
  *)
    # Not a memory path — pass through (allow)
    allow
    ;;
esac
