#!/bin/bash
# validate-post-hook — PostToolUse hook on Bash
#
# After the agent runs any validator script, this hook silently re-runs it
# with VALIDATE_LOCK=1 to manage the lock file. The agent doesn't know
# about the lock — it just sees validation pass or fail.
#
# Detection: looks for python/bash commands that include a canonical validator
# entrypoint under a `/validator/validate.{py,sh}` path and have a directory
# argument.

set -uo pipefail

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
[ "$TOOL" = "Bash" ] || exit 0

CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
[ -n "$CMD" ] || exit 0

# Only act on canonical validator entrypoints
echo "$CMD" | grep -Eq '/validator/validate\.(py|sh)( |$)' || exit 0

# Extract the script path — first match of a path ending in validator/validate.py or .sh
SCRIPT=$(echo "$CMD" | grep -oE '/[^ ]*/validator/validate\.(py|sh)' | head -1)
[ -n "$SCRIPT" ] || exit 0
[ -f "$SCRIPT" ] || exit 0

# Extract the directory argument — the path argument after the script
# Pattern: the script path followed by a space and then an absolute path
DIR_ARG=$(echo "$CMD" | sed "s|.*$SCRIPT||" | grep -oE '/[^ ]+' | head -1)
[ -n "$DIR_ARG" ] || exit 0
[ -d "$DIR_ARG" ] || exit 0

# Detect how to run the script
if [[ "$SCRIPT" == *.py ]]; then
    RUNNER="python3"
elif [[ "$SCRIPT" == *.sh ]]; then
    RUNNER="bash"
else
    RUNNER="python3"
fi

# Re-run with lock management (silent — output goes to /dev/null)
VALIDATE_LOCK=1 $RUNNER "$SCRIPT" "$DIR_ARG" > /dev/null 2>&1

exit 0
