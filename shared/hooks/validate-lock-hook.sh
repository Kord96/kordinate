#!/bin/bash
# validate-lock-hook — PreToolUse hook on Write/Edit
#
# Blocks writes to any directory containing a .validate-lock file.
# This is the generalized enforcement mechanism — any skill that uses
# warden's validate-output gets write-blocking for free.
#
# Lock lifecycle:
#   - Created by validate-post-hook.sh when a validator script fails
#   - Removed by validate-post-hook.sh when a validator script passes
#   - The agent never sees the lock — it sees "writes blocked, fix errors"

set -uo pipefail

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
[ "$TOOL" = "Write" ] || [ "$TOOL" = "Edit" ] || exit 0

# Get the target file path
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty')
[ -n "$FILE_PATH" ] || exit 0

# Only check writes to agent project memory directories ($MEM paths)
echo "$FILE_PATH" | grep -qE 'memory/projects/[^/]+/' || exit 0

# Extract the project memory directory root
MEM_DIR=$(echo "$FILE_PATH" | grep -oE '.*/memory/projects/[^/]+')
[ -n "$MEM_DIR" ] || exit 0

# Check for lock
LOCK="$MEM_DIR/.validate-lock"
if [ -f "$LOCK" ]; then
    ERRORS=$(cat "$LOCK")
    printf '{"error":"Write blocked: output validation has %s. To unblock: 1) Run the validator against %s  2) Read the errors  3) Fix them in the existing output files  4) Rerun validation  5) Once it passes, retry this write. Do NOT skip validation or delete files to work around this — fix the actual errors."}\n' "$ERRORS" "$MEM_DIR"
    exit 2
fi

exit 0
