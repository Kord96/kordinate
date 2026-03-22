#!/bin/bash
# Expiry check for scribe-default kord.
# Exit 0 = fresh (use cache), exit 1 = stale (re-invoke provider).
# Checks if provider's source files have changed since last consultation.

KORDINATE_HOME="${KORDINATE_HOME:-$(cd "$(dirname "$0")/../../.." && pwd)}"
source "$KORDINATE_HOME/lib/cache.sh"

KORD_DIR="$KORDINATE_HOME/agents/root/kords/scribe-default"
PROVIDER_DIR="$KORDINATE_HOME/agents/scribe"
CACHE_FILE="$KORD_DIR/.cache-hash"

# Check if consultation result exists
CONSULT_PATTERN="$KORDINATE_HOME/agents/root/memory/dynamic/consultations/scribe-default.md"
[ -f "$CONSULT_PATTERN" ] || exit 1  # no cache exists

# Check if provider's source files changed since last consultation
cache_check "$CACHE_FILE" "$PROVIDER_DIR" || exit 1

exit 0  # fresh
