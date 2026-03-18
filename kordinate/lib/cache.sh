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
