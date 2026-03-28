#!/bin/bash
# Manifest library for kordinate package tracking.
# Source this file — do not execute directly.
#
# Tracks which files were installed from a package source, their hashes,
# and whether the user has modified them. Enables safe updates: overwrite
# package files, preserve user customizations.
#
# Dependencies: sha256sum, jq (standard on all supported platforms)

# Files and directories excluded from manifest tracking.
_MANIFEST_EXCLUDE=(".git" ".manifest.json" ".dev-source" ".gitignore")

# manifest_hash <file>
# Return sha256 hash of a file.
manifest_hash() {
  local file="$1"
  [ -f "$file" ] || return 1
  sha256sum "$file" | cut -d' ' -f1
}

# _manifest_should_exclude <relative_path>
# Return 0 if the path should be excluded from tracking.
_manifest_should_exclude() {
  local rel="$1"
  for excl in "${_MANIFEST_EXCLUDE[@]}"; do
    case "$rel" in
      "$excl"|"$excl/"*) return 0 ;;
    esac
  done
  return 1
}

# _manifest_is_curated <file>
# Return 0 if file has curated: true in YAML frontmatter.
# Only checks .md files; everything else returns 1 (not curated).
_manifest_is_curated() {
  local file="$1"
  case "$file" in
    *.md) ;;
    *) return 1 ;;
  esac
  [ -f "$file" ] || return 1
  # Read up to the closing --- of frontmatter, look for curated: true
  local in_fm=0
  while IFS= read -r line; do
    if [ "$in_fm" -eq 0 ]; then
      [ "$line" = "---" ] && in_fm=1
      continue
    fi
    [ "$line" = "---" ] && break
    case "$line" in
      "curated: true"|"curated: true "*)
        return 0 ;;
    esac
  done < "$file"
  return 1
}

# manifest_init <kordinate_home> <source_type> <source_path_or_url> [--dev]
# Create .manifest.json by scanning all files in $KORDINATE_HOME.
# source_type: "local" or "remote"
manifest_init() {
  local kord_home="$1"
  local source_type="$2"
  local source_ref="$3"
  local dev_mode=false

  [ "${4:-}" = "--dev" ] && dev_mode=true

  local manifest="$kord_home/.manifest.json"
  local now
  now=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  # Build file entries by scanning kordinate home
  local entries="[]"
  while IFS= read -r file; do
    [ -n "$file" ] || continue
    local rel="${file#"$kord_home"/}"
    _manifest_should_exclude "$rel" && continue

    local hash curated
    hash=$(manifest_hash "$file")
    if _manifest_is_curated "$file"; then
      curated=true
    else
      curated=false
    fi

    entries=$(echo "$entries" | jq \
      --arg path "$rel" \
      --arg hash "$hash" \
      --argjson curated "$curated" \
      '. + [{"path": $path, "hash": $hash, "curated": $curated}]')
  done < <(find "$kord_home" -type f 2>/dev/null | sort)

  # Write manifest
  jq -n \
    --arg source_type "$source_type" \
    --arg source_ref "$source_ref" \
    --argjson dev_mode "$dev_mode" \
    --arg created "$now" \
    --arg updated "$now" \
    --argjson files "$entries" \
    '{
      source: {type: $source_type, ref: $source_ref},
      dev_mode: $dev_mode,
      created: $created,
      updated: $updated,
      files: $files
    }' > "$manifest"

  echo "Manifest created: $(echo "$entries" | jq length) files tracked"
}

# manifest_read <kordinate_home>
# Read .manifest.json, output to stdout.
manifest_read() {
  local kord_home="$1"
  local manifest="$kord_home/.manifest.json"
  if [ ! -f "$manifest" ]; then
    echo "No manifest found at $manifest" >&2
    return 1
  fi
  cat "$manifest"
}

# manifest_is_dev <kordinate_home>
# Return 0 if dev mode active, 1 otherwise.
manifest_is_dev() {
  local kord_home="$1"
  local manifest="$kord_home/.manifest.json"
  [ -f "$manifest" ] || return 1
  local dev
  dev=$(jq -r '.dev_mode' "$manifest" 2>/dev/null)
  [ "$dev" = "true" ] && return 0
  return 1
}

# manifest_source <kordinate_home>
# Output the source path/url.
manifest_source() {
  local kord_home="$1"
  local manifest="$kord_home/.manifest.json"
  [ -f "$manifest" ] || return 1
  jq -r '.source.ref' "$manifest"
}

# manifest_update <kordinate_home> <package_dir>
# Compare package files against manifest and apply changes.
#
# Actions per file:
#   new         — file in package, not in manifest → copy, add to manifest
#   unchanged   — hash matches manifest → overwrite, update hash
#   modified    — hash differs, curated=true → overwrite, warn
#   user-edit   — hash differs, curated=false → skip, warn
#   removed     — in manifest, not in package, unmodified → remove
#   kept        — in manifest, not in package, modified → skip (user content)
#
# Outputs one line per action: <action> <path>
manifest_update() {
  local kord_home="$1"
  local pkg_dir="$2"
  local manifest="$kord_home/.manifest.json"

  if [ ! -f "$manifest" ]; then
    echo "No manifest found — run manifest_init first" >&2
    return 1
  fi

  local now
  now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local updated_files
  updated_files=$(jq '.files' "$manifest")
  local actions=()

  # Pass 1: process files in the package
  while IFS= read -r pkg_file; do
    [ -n "$pkg_file" ] || continue
    local rel="${pkg_file#"$pkg_dir"/}"
    _manifest_should_exclude "$rel" && continue

    local pkg_hash installed curated
    pkg_hash=$(manifest_hash "$pkg_file")
    installed="$kord_home/$rel"

    if _manifest_is_curated "$pkg_file"; then
      curated=true
    else
      curated=false
    fi

    # Look up in manifest
    local manifest_hash_val
    manifest_hash_val=$(echo "$updated_files" | jq -r \
      --arg path "$rel" '.[] | select(.path == $path) | .hash')

    if [ -z "$manifest_hash_val" ]; then
      # New file — not in manifest
      mkdir -p "$(dirname "$installed")"
      cp "$pkg_file" "$installed"
      updated_files=$(echo "$updated_files" | jq \
        --arg path "$rel" \
        --arg hash "$pkg_hash" \
        --argjson curated "$curated" \
        '. + [{"path": $path, "hash": $hash, "curated": $curated}]')
      actions+=("copied $rel")

    elif [ -f "$installed" ]; then
      local installed_hash
      installed_hash=$(manifest_hash "$installed")

      if [ "$installed_hash" = "$manifest_hash_val" ]; then
        # Unchanged since last install — safe to overwrite
        cp "$pkg_file" "$installed"
        updated_files=$(echo "$updated_files" | jq \
          --arg path "$rel" \
          --arg hash "$pkg_hash" \
          --argjson curated "$curated" \
          'map(if .path == $path then .hash = $hash | .curated = $curated else . end)')
        actions+=("updated $rel")

      elif [ "$curated" = "true" ]; then
        # User modified a curated file — overwrite with warning
        cp "$pkg_file" "$installed"
        updated_files=$(echo "$updated_files" | jq \
          --arg path "$rel" \
          --arg hash "$pkg_hash" \
          --argjson curated "$curated" \
          'map(if .path == $path then .hash = $hash | .curated = $curated else . end)')
        actions+=("overwritten $rel (curated, user edits replaced)")

      else
        # User modified a non-curated file — skip
        actions+=("skipped $rel (user-modified, keeping local version)")
      fi

    else
      # File in manifest but missing on disk — treat as new
      mkdir -p "$(dirname "$installed")"
      cp "$pkg_file" "$installed"
      updated_files=$(echo "$updated_files" | jq \
        --arg path "$rel" \
        --arg hash "$pkg_hash" \
        --argjson curated "$curated" \
        'map(if .path == $path then .hash = $hash | .curated = $curated else . end)')
      actions+=("restored $rel")
    fi
  done < <(find "$pkg_dir" -type f 2>/dev/null | sort)

  # Pass 2: handle files removed from package (in manifest, not in package)
  local manifest_paths
  manifest_paths=$(echo "$updated_files" | jq -r '.[].path')
  while IFS= read -r rel; do
    [ -n "$rel" ] || continue
    local pkg_file="$pkg_dir/$rel"
    local installed="$kord_home/$rel"

    # Skip if file still exists in package
    [ -f "$pkg_file" ] && continue

    if [ -f "$installed" ]; then
      local installed_hash manifest_hash_val
      installed_hash=$(manifest_hash "$installed")
      manifest_hash_val=$(echo "$updated_files" | jq -r \
        --arg path "$rel" '.[] | select(.path == $path) | .hash')

      if [ "$installed_hash" = "$manifest_hash_val" ]; then
        # Unmodified — safe to remove
        rm "$installed"
        updated_files=$(echo "$updated_files" | jq \
          --arg path "$rel" 'map(select(.path != $path))')
        actions+=("removed $rel (no longer in package)")
      else
        # Modified — keep it
        actions+=("kept $rel (removed from package but locally modified)")
      fi
    else
      # Already gone from disk — clean up manifest entry
      updated_files=$(echo "$updated_files" | jq \
        --arg path "$rel" 'map(select(.path != $path))')
    fi
  done <<< "$manifest_paths"

  # Write updated manifest
  local updated_manifest
  updated_manifest=$(jq --arg updated "$now" --argjson files "$updated_files" \
    '.updated = $updated | .files = $files' "$manifest")
  echo "$updated_manifest" > "$manifest"

  # Output actions
  for action in "${actions[@]}"; do
    echo "$action"
  done
}
