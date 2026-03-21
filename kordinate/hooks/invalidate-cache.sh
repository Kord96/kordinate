#!/bin/bash
# PostToolUse hook: after Edit/Write, detect which agent owns the modified file,
# then delete .valid markers from all kords where that agent is provider.

INPUT=$(cat)

# Extract file_path from tool_input
FILE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)

if [ -z "$FILE" ]; then
  echo '{}'
  exit 0
fi

KORDINATE_HOME="${KORDINATE_HOME:-$(cd "$(dirname "$0")/.." && pwd)}"
KORDS_DIR="$KORDINATE_HOME/agents/root/kords"

agent=""

# Determine which agent owns the modified file
if [[ "$FILE" == *agents/deployer/* ]]; then
  agent="deployer"
elif [[ "$FILE" == *agents/designer/* ]]; then
  agent="designer"
elif [[ "$FILE" == *agents/sauron/* ]]; then
  agent="sauron"
elif [[ "$FILE" == *agents/scribe/* ]]; then
  agent="scribe"
# Deployer's extended sources: manifests/ and profile/
elif [[ "$FILE" == */manifests/* ]] || [[ "$FILE" == */profile/* ]]; then
  agent="deployer"
fi

if [ -z "$agent" ]; then
  echo '{}'
  exit 0
fi

# Find all kords where this agent is the provider and delete .valid markers
invalidated=0
for kord_dir in "$KORDS_DIR"/*/; do
  [ -d "$kord_dir" ] || continue
  kord_md="$kord_dir/kord.md"
  [ -f "$kord_md" ] || continue

  # Read provider from frontmatter
  provider=$(grep "^provider:" "$kord_md" 2>/dev/null | awk '{print $2}' | tr -d '[:space:]')
  if [ "$provider" = "$agent" ]; then
    valid_marker="$kord_dir/.valid"
    if [ -f "$valid_marker" ]; then
      rm -f "$valid_marker"
      invalidated=$((invalidated + 1))
    fi
  fi
done

if [ $invalidated -gt 0 ]; then
  echo "{\"hookSpecificOutput\":{\"message\":\"Invalidated $invalidated kord(s) for agent '$agent' due to change in $FILE\"}}"
else
  echo '{}'
fi
exit 0
