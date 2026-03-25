#!/bin/bash
# Generate KORD.md and KORD.json from frontmatter across all kordinate files
# Level 3 resource for the remember skill
# Usage: $KORDINATE_HOME/agents/scribe/skills/remember/generate-kord.sh [scope]
#   scope: "global" (default) or "project"

SCOPE="${1:-global}"

if [ "$SCOPE" = "global" ]; then
  ROOT="${KORDINATE_HOME:-$HOME/.kord}"
else
  ROOT=".kord"
fi

[ -d "$ROOT" ] || { echo "Directory $ROOT not found" >&2; exit 1; }

OUTPUT_MD="$ROOT/KORD.md"
OUTPUT_JSON="$ROOT/KORD.json"

# --- Helper: extract frontmatter value ---
fm_val() {
  sed -n "s/^$1: *//p" "$2" | head -1
}

# --- Generate KORD.md ---
echo "# KORD" > "$OUTPUT_MD"
echo "" >> "$OUTPUT_MD"
echo "Auto-generated from frontmatter. Do not edit manually." >> "$OUTPUT_MD"

# --- Generate KORD.json ---
echo "[" > "$OUTPUT_JSON"
FIRST=true

add_entry() {
  local file="$1"
  local rel="${file#$ROOT/}"
  local desc=$(fm_val "description" "$file")
  local curated=$(fm_val "curated" "$file")
  local preloaded=$(fm_val "preloaded" "$file")
  local template=$(fm_val "template" "$file")
  local owner=$(fm_val "owner" "$file")
  local scope=$(fm_val "scope" "$file")
  local expiry=$(fm_val "expiry" "$file")

  [ -z "$desc" ] && return

  # JSON entry
  if [ "$FIRST" = true ]; then
    FIRST=false
  else
    echo "," >> "$OUTPUT_JSON"
  fi

  printf '  {"path":"%s","description":"%s"' "$rel" "$desc" >> "$OUTPUT_JSON"
  [ -n "$curated" ] && [ "$curated" != "false" ] && printf ',"curated":%s' "$curated" >> "$OUTPUT_JSON"
  [ -n "$preloaded" ] && [ "$preloaded" != "none" ] && printf ',"preloaded":"%s"' "$preloaded" >> "$OUTPUT_JSON"
  [ -n "$template" ] && [ "$template" != "none" ] && printf ',"template":"%s"' "$template" >> "$OUTPUT_JSON"
  [ -n "$owner" ] && [ "$owner" != "agent" ] && printf ',"owner":"%s"' "$owner" >> "$OUTPUT_JSON"
  [ -n "$scope" ] && [ "$scope" != "global" ] && printf ',"scope":"%s"' "$scope" >> "$OUTPUT_JSON"
  [ -n "$expiry" ] && [ "$expiry" != "none" ] && printf ',"expiry":"%s"' "$expiry" >> "$OUTPUT_JSON"
  printf '}' >> "$OUTPUT_JSON"
}

# Agents
agents=$(find "$ROOT/agents" -iname "identity.md" 2>/dev/null | sort)
if [ -n "$agents" ]; then
  echo "" >> "$OUTPUT_MD"
  echo "## Agents" >> "$OUTPUT_MD"
  echo "" >> "$OUTPUT_MD"
  for f in $agents; do
    rel=${f#$ROOT/}
    desc=$(fm_val "description" "$f")
    echo "- \`$rel\` — $desc" >> "$OUTPUT_MD"
    add_entry "$f"
  done
fi

# Agent memory (including scratchpad)
memories=$(find "$ROOT/agents" -path "*/memory/*.md" 2>/dev/null | sort)
if [ -n "$memories" ]; then
  echo "" >> "$OUTPUT_MD"
  echo "## Memory" >> "$OUTPUT_MD"
  echo "" >> "$OUTPUT_MD"
  for f in $memories; do
    desc=$(fm_val "description" "$f")
    rel=${f#$ROOT/}
    [ -n "$desc" ] && echo "- \`$rel\` — $desc" >> "$OUTPUT_MD"
    add_entry "$f"
  done
fi

# Kords
kords=$(find "$ROOT/kords" -name "contract.md" 2>/dev/null | sort)
if [ -n "$kords" ]; then
  echo "" >> "$OUTPUT_MD"
  echo "## Kords" >> "$OUTPUT_MD"
  echo "" >> "$OUTPUT_MD"
  for f in $kords; do
    desc=$(fm_val "description" "$f")
    rel=${f#$ROOT/}
    echo "- \`$rel\` — $desc" >> "$OUTPUT_MD"
    add_entry "$f"
  done
fi

# Shared
shared=$(find "$ROOT/shared" -name "*.md" 2>/dev/null | sort)
if [ -n "$shared" ]; then
  echo "" >> "$OUTPUT_MD"
  echo "## Shared" >> "$OUTPUT_MD"
  echo "" >> "$OUTPUT_MD"
  for f in $shared; do
    desc=$(fm_val "description" "$f")
    rel=${f#$ROOT/}
    [ -n "$desc" ] && echo "- \`$rel\` — $desc" >> "$OUTPUT_MD"
    add_entry "$f"
  done
fi

echo "" >> "$OUTPUT_JSON"
echo "]" >> "$OUTPUT_JSON"

echo "Generated $OUTPUT_MD"
echo "Generated $OUTPUT_JSON"
