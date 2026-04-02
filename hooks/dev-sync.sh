#!/bin/bash
# dev-sync.sh — git post-commit hook for kordinate developers
# Copies changed package files from the repo to $KORDINATE_HOME after each commit.
# Only active when dev mode is enabled (register runtime --dev).
#
# Install: symlink to .git/hooks/post-commit (or append if hook exists)
#   ln -sf ../../hooks/dev-sync.sh .git/hooks/post-commit
# Make executable: chmod +x hooks/dev-sync.sh

set -euo pipefail

KORD_HOME="${KORDINATE_HOME:-$HOME/.kord}"
DEV_SOURCE_FILE="$KORD_HOME/.dev-source"

# Only run if dev mode is active
[ -f "$DEV_SOURCE_FILE" ] || exit 0

# Only run if this is the registered dev repo
EXPECTED_REPO=$(cat "$DEV_SOURCE_FILE")
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
[ "$REPO_ROOT" = "$EXPECTED_REPO" ] || exit 0

MANIFEST="$KORD_HOME/.manifest.json"

# Get files changed in the last commit under kordinate/
CHANGED=$(git diff-tree --no-commit-id --name-only -r HEAD -- kordinate/ 2>/dev/null)
[ -z "$CHANGED" ] && exit 0

COPIED=0
REMOVED=0

for file in $CHANGED; do
    rel="${file#kordinate/}"
    dest="$KORD_HOME/$rel"
    src="$REPO_ROOT/$file"

    if [ -f "$src" ]; then
        # File exists in commit — copy it
        mkdir -p "$(dirname "$dest")"
        cp "$src" "$dest"
        COPIED=$((COPIED + 1))
    elif [ -f "$dest" ]; then
        # File was deleted in commit — remove from installation if it's a package file
        if [ -f "$MANIFEST" ] && jq -e ".files[\"$rel\"]" "$MANIFEST" >/dev/null 2>&1; then
            rm "$dest"
            REMOVED=$((REMOVED + 1))
        fi
    fi
done

# Update manifest hashes for changed files
if [ -f "$MANIFEST" ] && command -v jq >/dev/null 2>&1; then
    for file in $CHANGED; do
        rel="${file#kordinate/}"
        dest="$KORD_HOME/$rel"
        if [ -f "$dest" ]; then
            hash=$(sha256sum "$dest" | cut -d' ' -f1)
            # Update hash in manifest
            tmp=$(mktemp)
            jq ".files[\"$rel\"].sha256 = \"$hash\" | .updated_at = \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"" "$MANIFEST" > "$tmp" && mv "$tmp" "$MANIFEST"
        else
            # Remove from manifest if file was deleted
            tmp=$(mktemp)
            jq "del(.files[\"$rel\"])" "$MANIFEST" > "$tmp" && mv "$tmp" "$MANIFEST"
        fi
    done
fi

# Update source ref to current commit
if [ -f "$MANIFEST" ] && command -v jq >/dev/null 2>&1; then
    REF=$(git rev-parse --short HEAD)
    tmp=$(mktemp)
    jq ".source.ref = \"$REF\"" "$MANIFEST" > "$tmp" && mv "$tmp" "$MANIFEST"
fi

echo "[kordinate] dev-sync: $COPIED copied, $REMOVED removed" >&2
