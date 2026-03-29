#!/bin/bash
# validate-post-hook — PostToolUse hook on Bash
#
# After the agent runs validate_output.py, this hook silently re-runs it
# with VALIDATE_LOCK=1 to manage the lock file. The agent doesn't know
# about the lock — it just sees validation pass or fail.

set -uo pipefail

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
[ "$TOOL" = "Bash" ] || exit 0

CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
[ -n "$CMD" ] || exit 0

# Only act on validate_output.py runs
echo "$CMD" | grep -q 'validate_output.py' || exit 0

# Extract the memory dir argument
MEM_DIR=$(echo "$CMD" | grep -oE '/[^ ]+' | head -1)
[ -n "$MEM_DIR" ] || exit 0
[ -d "$MEM_DIR" ] || exit 0

# Re-run with lock management (silent — output goes to /dev/null)
VALIDATE_LOCK=1 python3 "$(dirname "$0")/validate_output.py" "$MEM_DIR" > /dev/null 2>&1

exit 0
