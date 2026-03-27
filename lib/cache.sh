#!/bin/bash
# Shared cache library for hash-based cache invalidation.
# Source this file — do not execute directly.

# cache_hash <dir1> [dir2] ...
# Computes a deterministic hash of all files under the given directories.
cache_hash() {
  find "$@" -type f 2>/dev/null | sort | xargs cat 2>/dev/null | md5sum | cut -d' ' -f1
}

# cache_check <hash_file> <dir1> [dir2] ...
# Returns 0 if cache is fresh (hash matches), 1 if stale or missing.
cache_check() {
  local hash_file="$1"; shift
  local current_hash stored_hash
  current_hash=$(cache_hash "$@")
  stored_hash=$(cat "$hash_file" 2>/dev/null)
  [ "$current_hash" = "$stored_hash" ]
}

# cache_store <hash_file> <dir1> [dir2] ...
# Stores the current hash of source directories.
cache_store() {
  local hash_file="$1"; shift
  cache_hash "$@" > "$hash_file"
}

# cache_invalidate <hash_file>
# Removes the hash file to force regeneration on next check.
cache_invalidate() {
  rm -f "$1"
}

# cache_snapshot <snapshot_file> <path1> [path2] ...
# Store file listing with line counts and md5 hashes.
# Used by kord-expiry.sh to measure change magnitude.
cache_snapshot() {
  local snapshot_file="$1"; shift
  > "$snapshot_file"
  for path in "$@"; do
    if [ -d "$path" ]; then
      find "$path" -type f \( -name "*.md" -o -name "*.yaml" -o -name "*.yml" \
        -o -name "*.json" -o -name "*.sh" -o -name "*.js" \) 2>/dev/null | sort | while read -r f; do
        local lines hash
        lines=$(wc -l < "$f" 2>/dev/null || echo 0)
        hash=$(md5sum "$f" 2>/dev/null | cut -d' ' -f1)
        echo "$lines $hash $f" >> "$snapshot_file"
      done
    elif [ -f "$path" ]; then
      local lines hash
      lines=$(wc -l < "$path" 2>/dev/null || echo 0)
      hash=$(md5sum "$path" 2>/dev/null | cut -d' ' -f1)
      echo "$lines $hash $path" >> "$snapshot_file"
    fi
  done
}
