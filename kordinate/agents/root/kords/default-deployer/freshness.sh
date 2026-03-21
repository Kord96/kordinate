#!/bin/bash
# Check if default-deployer kord result is still fresh.
# Exit 0 = fresh (use cached), exit 1 = stale (re-consult).

KORDINATE_HOME="${KORDINATE_HOME:-$(cd "$(dirname "$0")/../../.." && pwd)}"
KORD_NAME="default-deployer"
PROVIDER="deployer"

VALID_MARKER="$KORDINATE_HOME/agents/root/kords/$KORD_NAME/.valid"

if [ -f "$VALID_MARKER" ]; then
  exit 0  # fresh
fi

exit 1  # stale
