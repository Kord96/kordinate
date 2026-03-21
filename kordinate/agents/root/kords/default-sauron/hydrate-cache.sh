#!/bin/bash
# Cache management for default-sauron kord.
# Pre-consult:  exit 0 = fresh (use cached), exit 1 = stale (re-invoke).
# Post-consult: called with "store" arg to reset freshness state.

KORDINATE_HOME="${KORDINATE_HOME:-$(cd "$(dirname "$0")/../../.." && pwd)}"
KORD_NAME="default-sauron"
VALID_MARKER="$KORDINATE_HOME/agents/root/kords/$KORD_NAME/.valid"

# Post-consult: store freshness state
if [ "${1:-}" = "store" ]; then
  touch "$VALID_MARKER"
  exit 0
fi

# Pre-consult: check freshness
if [ -f "$VALID_MARKER" ]; then
  exit 0  # fresh
fi

exit 1  # stale
