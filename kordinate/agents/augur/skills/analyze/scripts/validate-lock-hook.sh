#!/bin/bash
# validate-lock-hook — PreToolUse hook on Write/Edit
#
# Blocks writes to augur memory directories when a validation lock exists.
# The lock is created by validate_output.py --lock when validation fails,
# and removed when validation succeeds.
#
# This forces the agent to fix validation errors before writing new output.
# Without the lock, writes proceed normally (no lock = no gate).

set -uo pipefail

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
[ "$TOOL" = "Write" ] || [ "$TOOL" = "Edit" ] || exit 0

# Get the target file path
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty')
[ -n "$FILE_PATH" ] || exit 0

# Only check writes to augur memory directories
echo "$FILE_PATH" | grep -qE '\.kord/agents/augur/memory/' || exit 0

# Find the memory directory root
MEM_DIR=$(echo "$FILE_PATH" | grep -oE '.*/\.kord/agents/augur/memory')
[ -n "$MEM_DIR" ] || exit 0

# Check for lock
LOCK="$MEM_DIR/.validate-lock"
if [ -f "$LOCK" ]; then
    ERRORS=$(cat "$LOCK")
    printf '{"error":"Validation lock active (%s). Run validate_output.py to see errors, fix them, then revalidate. The lock is removed when validation passes."}\n' "$ERRORS"
    exit 2
fi

exit 0
