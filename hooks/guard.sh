#!/bin/bash
# Unified guard for kordinate
#
# Primary guard for the current pod-agent runtime path. This hook uses dedicated
# guard logic and replaces the removed KORD-driven compatibility path.
#
# Enforces domain boundaries:
#   deployer → git push (test/prod), kubectl writes
#   sauron   → Grafana dashboards, API, MCP
#   merge    → git push to main (FF check — blocks if rebase needed)
#
# Registered in settings.json as PreToolUse on Write|Edit, Bash, mcp__grafana*
# See README.md for the full rules table.
# KORD-driven compatibility guard behavior has been removed from the primary runtime path.

set -uo pipefail

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
KORD_HOME="${KORDINATE_HOME:-$HOME/.kord}"
OWNERSHIP_FILE="${REPO_ROOT:-/kord/projects/kordinate}/shared/runtime-ownership.yaml"

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

lookup_runtime_owner() {
  local relative_path="$1"
  [ -f "$OWNERSHIP_FILE" ] || return 0
  OWNERSHIP_FILE="$OWNERSHIP_FILE" RELATIVE_PATH="$relative_path" python3 - <<'PY'
import os
from pathlib import Path
import yaml

ownership_file = Path(os.environ['OWNERSHIP_FILE'])
relative_path = os.environ['RELATIVE_PATH'].strip('/')
config = yaml.safe_load(ownership_file.read_text()) or {}
entries = config.get('protected_paths') or []
match = None
for entry in entries:
    path = str(entry.get('path', '')).strip('/')
    if not path:
        continue
    is_dir = entry.get('path', '').endswith('/')
    if is_dir:
        if relative_path.startswith(path):
            if match is None or len(path) > len(match.get('path', '')):
                match = entry
    elif relative_path == path:
        if match is None or len(path) > len(match.get('path', '')):
            match = entry
if match:
    print(match.get('owner', ''))
PY
}

# --- Write / Edit ---------------------------------------------------------

guard_write() {
  local file_path
  file_path=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
  [ -z "$file_path" ] && allow

  # config.yaml: field-level ACL — each YAML path has an owning agent
  case "$file_path" in
    */profile/config.yaml)
      local acl_file="$KORD_HOME/profile/config-acl.yaml"
      if [ -f "$acl_file" ]; then
        local old_str new_str
        old_str=$(echo "$INPUT" | jq -r '.tool_input.old_string // .tool_input.content // empty')
        new_str=$(echo "$INPUT" | jq -r '.tool_input.new_string // empty')
        local required_agent
        required_agent=$(ACL_FILE="$acl_file" CONFIG_FILE="$file_path" OLD_STR="$old_str" python3 -c "
import yaml, os

acl = yaml.safe_load(open(os.environ['ACL_FILE']))
config_file = os.environ['CONFIG_FILE']
old_str = os.environ.get('OLD_STR', '')

# Find which top-level key the edit falls under by locating old_str in the file
agents = set()
try:
    with open(config_file) as f:
        lines = f.readlines()
    # Find the line where old_str starts
    full = ''.join(lines)
    pos = full.find(old_str[:60])
    if pos >= 0:
        # Walk backwards to find the top-level key (no leading whitespace)
        before = full[:pos].splitlines()
        for line in reversed(before):
            if line and not line[0].isspace() and ':' in line:
                top_key = line.split(':')[0].strip()
                for path, agent in acl.items():
                    if path.split('.')[0] == top_key:
                        agents.add(agent)
                break
except Exception:
    pass

print(' '.join(sorted(agents)) if agents else '')
" 2>/dev/null)

        # Check if any matching agent is authenticated
        if [ -n "$required_agent" ]; then
          for agent in $required_agent; do
            check_auth "$agent" && allow
          done
          deny "config.yaml edit touches fields owned by: $required_agent. Authenticate as one of them."
        fi
      fi

      deny "config.yaml edit requires field-owner authentication."
      ;;
  esac

  # Protected runtime files under .kord/
  case "$file_path" in
    */.kord/*)
      local rel_path owner
      rel_path=$(echo "$file_path" | sed 's|.*\.kord/||')
      owner=$(lookup_runtime_owner "$rel_path")
      if [ -n "$owner" ]; then
        check_auth "$owner" && allow
        deny "This runtime-managed path is owned by $owner. Authenticate as $owner before editing it."
      fi
      allow
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
      if [ -z "$branch" ]; then
        local git_c_detect
        git_c_detect=$(echo "$cmd" | grep -oE 'git\s+-C\s+(\S+)' | awk '{print $NF}')
        git_c_detect="${git_c_detect/#\~/$HOME}"
        if [ -n "$git_c_detect" ]; then
          branch=$(git -C "$git_c_detect" branch --show-current 2>/dev/null || echo "unknown")
        else
          branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        fi
      fi

      # Resolve repo root: check -C <dir>, cd <dir>, or fall back to cwd
      local git_c_dir repo_root cd_dir
      git_c_dir=$(echo "$cmd" | grep -oE 'git\s+-C\s+(\S+)' | awk '{print $NF}')
      if [ -z "$git_c_dir" ]; then
        cd_dir=$(echo "$cmd" | grep -oE '^\s*cd\s+(\S+)' | awk '{print $NF}')
        cd_dir="${cd_dir/#\~/$HOME}"
      else
        git_c_dir="${git_c_dir/#\~/$HOME}"
      fi
      if [ -n "$git_c_dir" ]; then
        repo_root=$(git -C "$git_c_dir" rev-parse --show-toplevel 2>/dev/null)
      elif [ -n "$cd_dir" ]; then
        repo_root=$(git -C "$cd_dir" rev-parse --show-toplevel 2>/dev/null)
      else
        repo_root=$(git rev-parse --show-toplevel 2>/dev/null)
      fi

      case "$branch" in
        main)
          # Allow if /integrate is running (lock exists)
          [ -n "$repo_root" ] && [ -d "$repo_root/.integrate-lock" ] && allow
          # Allow if fast-forward is possible
          if [ -n "$repo_root" ]; then
            git -C "$repo_root" fetch origin main 2>/dev/null
            if git -C "$repo_root" merge-base --is-ancestor origin/main HEAD 2>/dev/null; then
              allow
            fi
          fi
          deny "Push to main blocked — your branch has diverged from main. Use /integrate to reconcile and resolve."
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
        # Hard-block: self-modifying the workstation deployment or draining nodes
        if echo "$cmd" | grep -qE 'deploy(ment)?[/ ]workstation|kubectl\s+drain|kubectl\s+cordon'; then
          deny "Blocked: workstation deployment self-modification and node drain are never allowed from inside the pod."
        fi
        check_auth deployer && allow
        deny "kubectl write operations require deployer authentication. Use /infra."
      fi
      ;;
  esac

  # Grafana API — match admin operations (dashboard writes, provisioning), not health checks or proxying
  if echo "$cmd" | grep -qE ':(30300|3000)/api/(dashboards|datasources|provisioning|admin|annotations)|grafana_admin'; then
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
