#!/bin/bash
# Unified guard for kordinate — data-driven from KORD.json
#
# Reads KORD.json entries to enforce:
#   type: "file"  → who can write to which paths (validation field)
#   type: "guard" → which Bash/MCP commands need agent auth
#
# No hardcoded rules except: KORD.json itself (handled by warden entry in KORD.json).
#
# Registered in settings.json as PreToolUse on Write|Edit|Bash|mcp*

set -uo pipefail

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
KORD_HOME="${KORDINATE_HOME:-$HOME/.kord}"
KORD_JSON="$KORD_HOME/KORD.json"

allow() { echo '{}'; exit 0; }

deny() {
  local reason="$1"
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}' "$reason"
  exit 0
}

check_auth() {
  local agent="$1"
  local auth_file="/tmp/.${agent}-auth"
  local lock_file="$KORD_HOME/profile/locks/${agent}"
  [ -f "$auth_file" ] && [ -f "$lock_file" ] || return 1
  [ "$(cat "$auth_file")" = "$(cat "$lock_file")" ]
}

# No KORD.json = no guards
[ -f "$KORD_JSON" ] || allow

# --- Write / Edit ---------------------------------------------------------

guard_write() {
  local file_path
  file_path=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
  [ -z "$file_path" ] && allow

  # Only guard .kord/ paths
  echo "$file_path" | grep -qE '\.kord/' || allow

  # Extract relative path within kordinate
  local rel_path
  rel_path=$(echo "$file_path" | sed 's|.*\.kord/||')
  [ -z "$rel_path" ] && allow

  # Look up in KORD.json — find the most specific matching file entry
  # Matches both exact paths and directory prefixes
  local validation
  validation=$(jq -r --arg p "$rel_path" '
    [.[] | select(.type == "file" and .path != null and ($p | startswith(.path)))]
    | sort_by(-.path | length)
    | .[0].validation // empty
  ' "$KORD_JSON" 2>/dev/null)

  # No matching entry = no protection
  [ -z "$validation" ] && allow

  # Validation is an agent name — check auth
  if echo "$validation" | grep -qE '^[a-z]+$'; then
    check_auth "$validation" && allow
    deny "This file requires $validation authorization. Use /authenticate $validation or delegate via /kord $validation."
  fi

  # Validation is a script path — allow write, warden validates post-hoc
  allow
}

# --- Bash -----------------------------------------------------------------

guard_bash() {
  local cmd
  cmd=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
  [ -z "$cmd" ] && allow

  # Read all Bash guard entries
  local guards
  guards=$(jq -c '[.[] | select(.type == "guard" and .tool == "Bash")]' "$KORD_JSON" 2>/dev/null)
  [ -z "$guards" ] || [ "$guards" = "[]" ] && allow

  # Check each guard pattern
  while IFS= read -r guard; do
    local pattern validation description
    pattern=$(echo "$guard" | jq -r '.pattern // empty')
    validation=$(echo "$guard" | jq -r '.validation // empty')
    description=$(echo "$guard" | jq -r '.description // empty')

    [ -z "$pattern" ] && continue

    # Match command against pattern
    if echo "$cmd" | grep -qE "$pattern"; then
      # Special: merge validation = just block force push
      if [ "$validation" = "merge" ]; then
        echo "$cmd" | grep -q '\-\-force\|\-f ' && \
          deny "Force push to main is not allowed. Use /merge to resolve conflicts."
        allow
      fi

      # Agent validation — check auth
      check_auth "$validation" && allow
      deny "$description. Use /authenticate $validation or delegate via /kord $validation."
    fi
  done < <(echo "$guards" | jq -c '.[]')

  allow
}

# --- MCP ------------------------------------------------------------------

guard_mcp() {
  local tool_name
  tool_name=$(echo "$INPUT" | jq -r '.tool_name // empty')
  [ -z "$tool_name" ] && allow

  # Read all MCP guard entries
  local guards
  guards=$(jq -c '[.[] | select(.type == "guard" and .tool == "mcp")]' "$KORD_JSON" 2>/dev/null)
  [ -z "$guards" ] || [ "$guards" = "[]" ] && allow

  while IFS= read -r guard; do
    local pattern validation description
    pattern=$(echo "$guard" | jq -r '.pattern // empty')
    validation=$(echo "$guard" | jq -r '.validation // empty')
    description=$(echo "$guard" | jq -r '.description // empty')

    [ -z "$pattern" ] && continue

    if echo "$tool_name" | grep -qE "$pattern"; then
      check_auth "$validation" && allow
      deny "$description. Use /authenticate $validation."
    fi
  done < <(echo "$guards" | jq -c '.[]')

  allow
}

# --- Route ----------------------------------------------------------------

case "$TOOL" in
  Write|Edit) guard_write ;;
  Bash)       guard_bash ;;
  mcp__*)     guard_mcp ;;
  *)          allow ;;
esac
