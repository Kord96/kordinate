#!/bin/bash
# PostToolUse hook: after Edit/Write, check if the modified file falls within
# an agent's declared cache source dirs. If so, invalidate all consultation
# caches where that agent is the consultant.

INPUT=$(cat)

# Extract file_path from tool_input
FILE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)

if [ -z "$FILE" ]; then
  echo '{}'
  exit 0
fi

KORDINATE_HOME="${KORDINATE_HOME:-$(cd "$(dirname "$0")/.." && pwd)}"
AGENTS_DIR="$KORDINATE_HOME/agents"

agent=""

# Determine which agent owns the modified file by checking if path is under agents/<agent>/
if [[ "$FILE" == *agents/deployer/* ]]; then
  agent="deployer"
elif [[ "$FILE" == *agents/designer/* ]]; then
  agent="designer"
elif [[ "$FILE" == *agents/sauron/* ]]; then
  agent="sauron"
elif [[ "$FILE" == *agents/scribe/* ]]; then
  agent="scribe"
# Deployer's extended cache sources: manifests/ and profile/
elif [[ "$FILE" == */manifests/* ]] || [[ "$FILE" == */profile/* ]]; then
  agent="deployer"
fi

if [ -z "$agent" ]; then
  echo '{}'
  exit 0
fi

# Read the agent's consultation.md to find Cache Sources
CONSULTATION="$AGENTS_DIR/$agent/instructions/consultation.md"
if [ ! -f "$CONSULTATION" ]; then
  echo '{}'
  exit 0
fi

# Parse cache source dirs from the ## Cache Sources section
in_cache_section=false
cache_dirs=()
while IFS= read -r line; do
  if [[ "$line" == "## Cache Sources"* ]]; then
    in_cache_section=true
    continue
  fi
  if $in_cache_section; then
    # Stop at the next section header
    if [[ "$line" == "##"* ]] && [[ "$line" != "## Cache Sources"* ]]; then
      break
    fi
    # Extract directory paths from markdown list items: - `path/`
    if [[ "$line" =~ ^-\ \`(.+)\` ]]; then
      cache_dirs+=("${BASH_REMATCH[1]}")
    fi
  fi
done < "$CONSULTATION"

if [ ${#cache_dirs[@]} -eq 0 ]; then
  echo '{}'
  exit 0
fi

# Check if the modified file falls within any declared cache source dir
matched=false
for dir in "${cache_dirs[@]}"; do
  # Handle relative paths like ../../profile/config.yaml
  if [[ "$dir" == ../../* ]]; then
    # Resolve relative to agents/<agent>/instructions/
    resolved=$(cd "$AGENTS_DIR/$agent/instructions" 2>/dev/null && cd "$(dirname "$dir")" 2>/dev/null && pwd)/$(basename "$dir")
    if [[ "$FILE" == "$resolved"* ]] || [[ "$FILE" == *"$(basename "$(dirname "$resolved")")/$(basename "$resolved")"* ]]; then
      matched=true
      break
    fi
  else
    # dir is relative to the agent's root: agents/<agent>/<dir>
    if [[ "$FILE" == *"agents/$agent/$dir"* ]]; then
      matched=true
      break
    fi
  fi
done

if ! $matched; then
  echo '{}'
  exit 0
fi

# Invalidate all consultation caches where this agent is the consultant
invalidated=0
for hash_file in "$KORDINATE_HOME/agents/shared/memory/dynamic"/.*-${agent}.hash; do
  [ -f "$hash_file" ] || continue
  rm -f "$hash_file"
  invalidated=$((invalidated + 1))
done

if [ $invalidated -gt 0 ]; then
  echo "{\"hookSpecificOutput\":{\"message\":\"Invalidated $invalidated consultation cache(s) for agent '$agent' due to change in $FILE\"}}"
else
  echo '{}'
fi
exit 0
