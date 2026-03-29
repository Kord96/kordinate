#!/bin/bash
# validate-lock-hook — PreToolUse hook on Write/Edit
#
# Blocks writes to augur memory directories when output validation has failed.
# On first write after a validation failure, the agent sees an error message
# telling it to fix validation issues. The agent does not know about the lock
# mechanism — it only knows that writes are blocked until validation passes.
#
# Lock lifecycle:
#   - Created by validate_output.py --lock when validation fails
#   - Removed by validate_output.py --lock when validation succeeds
#   - The skill procedure tells the agent to "run validation and fix errors"
#   - The agent runs validate_output.py (without --lock), which it sees as
#     a normal check. The hook infrastructure separately manages the lock.

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
    printf '{"error":"Output validation failed (%s). Fix the validation errors reported by validate_output.py and rerun it before writing more output."}\n' "$ERRORS"
    exit 2
fi

exit 0
