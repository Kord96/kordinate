#!/bin/bash
# Hash-based cache expiry for project-analysis kord.
# Receives project path as $1. Exit 0 = fresh, exit 1 = stale.
KORD_DIR="$(cd "$(dirname "$0")" && pwd)"
KORDINATE_HOME="${KORDINATE_HOME:-$HOME/.kord}"
source "$KORDINATE_HOME/lib/cache.sh"

PROJECT="$1"
[ -n "$PROJECT" ] || exit 1

MEMORY="$PROJECT/.kord/agents/augur/memory"

# Check that architecture.yaml v2 exists (single artifact since v2)
[ -f "$MEMORY/architecture.yaml" ] || exit 1

# Build list of source directories that exist in the project
SRC_DIRS=()
for d in app src lib; do
  [ -d "$PROJECT/$d" ] && SRC_DIRS+=("$PROJECT/$d")
done

# Include manifest files if they exist
MANIFESTS=()
for f in package.json pyproject.toml go.mod Cargo.toml; do
  [ -f "$PROJECT/$f" ] && MANIFESTS+=("$PROJECT/$f")
done

# Must have at least some source to hash
[ ${#SRC_DIRS[@]} -eq 0 ] && [ ${#MANIFESTS[@]} -eq 0 ] && exit 1

# Per-project hash file based on project path
HASH_SLUG=$(echo "$PROJECT" | md5sum | cut -c1-8)
HASH_FILE="$KORD_DIR/.hash-$HASH_SLUG"

# Check input hash — stale if project sources changed since last analysis
cache_check "$HASH_FILE" "${SRC_DIRS[@]}" "${MANIFESTS[@]}" \
  || exit 1

exit 0  # fresh
