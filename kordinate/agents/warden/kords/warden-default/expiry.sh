#!/bin/bash
# Expiry check. Exit 0 = fresh, exit 1 = stale.
KORD_DIR="$(cd "$(dirname "$0")" && pwd)"
KORDINATE_HOME="${KORDINATE_HOME:-$HOME/.kord}"

# Check if cached data exists
[ -f "$KORD_DIR/data.md" ] || exit 1

# Check .valid marker
[ -f "$KORD_DIR/.valid" ] || exit 1

exit 0  # fresh
