#!/bin/bash
# Unified guard for kordinate
#
# Enforces domain boundaries:
#   scribe   → curated .kord/ files
#   deployer → git push (test/prod), kubectl writes
#   sauron   → Grafana dashboards, API, MCP
#   merge    → git push to main (FF check — blocks if rebase needed)
#
# Registered in settings.json as PreToolUse on Write|Edit, Bash, mcp__grafana*
# See README.md for the full rules table.

set -uo pipefail

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
KORD_HOME="${KORDINATE_HOME:-$HOME/.kord}"

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

# --- Write / Edit ---------------------------------------------------------

guard_write() {
  local file_path
  file_path=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
  [ -z "$file_path" ] && allow

  # Scribe: curated .kord/ files only
  case "$file_path" in
    */.kord/*)
      check_auth scribe && allow

      # Allow non-curated, non-templated files without auth
      local kord_json="$KORD_HOME/KORD.json"
      if [ -f "$kord_json" ]; then
        local entry
        entry=$(jq -r --arg p "$file_path" \
          '.[] | select(.path and ($p | endswith(.path)))' \
          "$kord_json" 2>/dev/null)
        if [ -n "$entry" ]; then
          local curated template
          curated=$(echo "$entry" | jq -r '.curated // false')
          template=$(echo "$entry" | jq -r '.template // "none"')
          [ "$curated" = "false" ] && [ "$template" = "none" ] && allow
        fi
      fi

      deny "This file is managed by kordinate. Use /kord remember to write memories."
      ;;
  esac

  # Sauron: Grafana dashboards
  case "$file_path" in
    */dashboards/*.json|*/grafana*)
      check_auth sauron && allow
      deny "Dashboard edits require sauron authentication. Use /authenticate as sauron."
      ;;
  esac

  allow
}

# --- Bash -----------------------------------------------------------------

guard_bash() {
  local cmd
  cmd=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
  [ -z "$cmd" ] && allow

  # Git push
  case "$cmd" in
    *git\ push*|*git\ \ push*)
      local push_cmd branch
      push_cmd=$(echo "$cmd" | grep -oE 'git\s+push[^&;]*' | head -1)
      [ -z "$push_cmd" ] && allow

      branch=$(echo "$push_cmd" | grep -oE 'origin\s+(\S+)' | awk '{print $2}')
      branch=$(echo "$branch" | sed 's/.*://')
      [ -z "$branch" ] && branch=$(git branch --show-current 2>/dev/null || echo "unknown")

      case "$branch" in
        main)
          # Allow if /merge is running (lock exists)
          local repo_root
          repo_root=$(git rev-parse --show-toplevel 2>/dev/null)
          [ -d "$repo_root/.merge-lock" ] && allow
          # Allow if fast-forward is possible
          git fetch origin main 2>/dev/null
          if git merge-base --is-ancestor origin/main HEAD 2>/dev/null; then
            allow
          fi
          deny "Push to main blocked — your branch has diverged from main. Use /merge to rebase and resolve."
          ;;
        session/*|memory/*)
          allow
          ;;
        test|prod)
          check_auth deployer && allow
          deny "Push to '$branch' requires deployer authentication. Use /infra roll."
          ;;
      esac
      ;;
  esac

  # Kubectl writes
  case "$cmd" in
    *kubectl*)
      if echo "$cmd" | grep -qE 'kubectl\s+(apply|create|delete|patch|replace|scale|rollout|drain|cordon|uncordon|taint|label|annotate)'; then
        # Always blocked — even with auth
        if echo "$cmd" | grep -qE 'workstation|apply\s+-k\s+master/|kubectl\s+drain|kubectl\s+cordon'; then
          deny "Blocked: workstation and master namespace modifications are never allowed."
        fi
        check_auth deployer && allow
        deny "kubectl write operations require deployer authentication. Use /infra."
      fi
      ;;
  esac

  # Grafana API — only match network calls, not file operations mentioning "grafana"
  if echo "$cmd" | grep -qE '(curl|wget|ssh).*grafana|grafana.*(curl|wget|ssh)|:(30300|3000)/api'; then
    check_auth sauron && allow
    deny "Grafana operations require sauron authentication. Use /authenticate as sauron."
  fi

  allow
}

# --- MCP Grafana ----------------------------------------------------------

guard_grafana_mcp() {
  check_auth sauron && allow
  deny "Grafana MCP requires sauron authentication. Use /authenticate as sauron."
}

# --- Route ----------------------------------------------------------------

case "$TOOL" in
  Write|Edit)     guard_write ;;
  Bash)           guard_bash ;;
  mcp__grafana*)  guard_grafana_mcp ;;
  *)              allow ;;
esac
