#!/bin/bash
# Generate KORD.md from frontmatter across all kordinate files
# Level 3 resource for the remember skill
# Usage: $KORDINATE_HOME/agents/scribe/skills/remember/generate-kord.sh [scope]
#   scope: "global" (default) or "project"

SCOPE="${1:-global}"

if [ "$SCOPE" = "global" ]; then
  ROOT="${KORDINATE_HOME:-$HOME/.kord}"
  OUTPUT="$ROOT/KORD.md"
else
  ROOT=".kord"
  OUTPUT="$ROOT/KORD.md"
fi

[ -d "$ROOT" ] || { echo "Directory $ROOT not found" >&2; exit 1; }

echo "# KORD" > "$OUTPUT"
echo "" >> "$OUTPUT"
echo "Auto-generated from frontmatter. Do not edit manually." >> "$OUTPUT"

# Agents
agents=$(find "$ROOT/agents" -iname "identity.md" 2>/dev/null | sort)
if [ -n "$agents" ]; then
  echo "" >> "$OUTPUT"
  echo "## Agents" >> "$OUTPUT"
  echo "" >> "$OUTPUT"
  for f in $agents; do
    desc=$(sed -n 's/^description: *//p' "$f" | head -1)
    rel=${f#$ROOT/}
    echo "- \`$rel\` — $desc" >> "$OUTPUT"
  done
fi

# Agent memory
memories=$(find "$ROOT/agents" -path "*/memory/*.md" -not -name "scratchpad.md" 2>/dev/null | sort)
if [ -n "$memories" ]; then
  echo "" >> "$OUTPUT"
  echo "## Memory" >> "$OUTPUT"
  echo "" >> "$OUTPUT"
  for f in $memories; do
    desc=$(sed -n 's/^description: *//p' "$f" | head -1)
    rel=${f#$ROOT/}
    [ -n "$desc" ] && echo "- \`$rel\` — $desc" >> "$OUTPUT"
  done
fi

# Kords
kords=$(find "$ROOT/kords" -name "contract.md" 2>/dev/null | sort)
if [ -n "$kords" ]; then
  echo "" >> "$OUTPUT"
  echo "## Kords" >> "$OUTPUT"
  echo "" >> "$OUTPUT"
  for f in $kords; do
    desc=$(sed -n 's/^description: *//p' "$f" | head -1)
    rel=${f#$ROOT/}
    echo "- \`$rel\` — $desc" >> "$OUTPUT"
  done
fi

echo "Generated $OUTPUT"
