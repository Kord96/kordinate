#!/bin/bash
# Unified guard for kordinate workstation runtime.
set -uo pipefail

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
WORKSTATION_HOME="${WORKSTATION_HOME:-$HOME}"
KORD_SOURCE_ROOT="${KORD_SOURCE_ROOT:-$HOME/repos/kordinate}"
KORD_LOCAL_STATE="${KORD_LOCAL_STATE:-$HOME/.local/share/kordinate}"
KORD_LOCKS_DIR="${KORD_LOCKS_DIR:-$KORD_LOCAL_STATE/locks}"
KORD_PROFILE_STATE_DIR="${KORD_PROFILE_STATE_DIR:-$KORD_LOCAL_STATE/profile}"
OWNERSHIP_FILE="${REPO_ROOT:-$HOME/.claude/runtime-ownership.yaml}"

allow() { echo '{}'; exit 0; }

deny() {
  local reason="$1"
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}' "$reason"
  exit 0
}

check_auth() {
  local agent="$1"
  local auth_file="/tmp/.${agent}-auth"
  local lock_file="$KORD_LOCKS_DIR/${agent}"
  [ -f "$auth_file" ] && [ -f "$lock_file" ] || return 1
  [ "$(cat "$auth_file")" = "$(cat "$lock_file")" ]
}

lookup_runtime_owner() {
  local relative_path="$1"
  local acl_file="$KORD_PROFILE_STATE_DIR/config-acl.yaml"
  ACL_FILE="$acl_file" OWNERSHIP_FILE="$OWNERSHIP_FILE" RELATIVE_PATH="$relative_path" python3 - <<'PY'
import os
from pathlib import Path
import yaml

relative_path = os.environ['RELATIVE_PATH'].strip('/')
paths = []
acl_file = Path(os.environ['ACL_FILE'])
ownership_file = Path(os.environ['OWNERSHIP_FILE'])
if acl_file.exists():
    cfg = yaml.safe_load(acl_file.read_text()) or {}
    paths.extend(cfg.get('paths') or [])
if ownership_file.exists():
    cfg = yaml.safe_load(ownership_file.read_text()) or {}
    paths.extend(cfg.get('protected_paths') or [])
match = None
for entry in paths:
    path = str(entry.get('path', '')).strip('/')
    if not path:
        continue
    is_dir = str(entry.get('path', '')).endswith('/')
    if is_dir:
        if relative_path.startswith(path):
            if match is None or len(path) > len(str(match.get('path', ''))):
                match = entry
    elif relative_path == path:
        if match is None or len(path) > len(str(match.get('path', ''))):
            match = entry
if match:
    print(match.get('owner', ''))
PY
}

lookup_config_owner() {
  local file_path="$1"
  local old_str="$2"
  local acl_file="$KORD_PROFILE_STATE_DIR/config-acl.yaml"
  [ -f "$acl_file" ] || return 0
  ACL_FILE="$acl_file" CONFIG_FILE="$file_path" OLD_STR="$old_str" python3 - <<'PY'
import os
from pathlib import Path
import yaml

acl = yaml.safe_load(Path(os.environ['ACL_FILE']).read_text()) or {}
config_entries = acl.get('config') or []
config_file = os.environ['CONFIG_FILE']
old_str = os.environ.get('OLD_STR', '')
target = None
for entry in config_entries:
    if entry.get('file') == 'profile/config.yaml':
        target = entry
        break
if not target:
    raise SystemExit(0)
ownership = target.get('ownership') or {}
try:
    with open(config_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    full = ''.join(lines)
    pos = full.find(old_str[:60]) if old_str else -1
    if pos >= 0:
        before = full[:pos].splitlines()
        for line in reversed(before):
            if line and not line[0].isspace() and ':' in line:
                top_key = line.split(':')[0].strip()
                owner = ownership.get(top_key)
                if owner:
                    print(owner)
                break
except Exception:
    pass
PY
}

runtime_relative_path() {
  local file_path="$1"
  case "$file_path" in
    "$HOME/.claude"/*)
      printf '.claude/%s\n' "${file_path#"$HOME/.claude"/}"
      ;;
    "$KORD_LOCAL_STATE"/*)
      printf '.local/share/kordinate/%s\n' "${file_path#"$KORD_LOCAL_STATE"/}"
      ;;
    *)
      return 1
      ;;
  esac
}

repo_relative_path() {
  local file_path="$1"
  case "$file_path" in
    "$KORD_SOURCE_ROOT"/*)
      printf '%s\n' "${file_path#"$KORD_SOURCE_ROOT"/}"
      ;;
    *)
      return 1
      ;;
  esac
}

guard_write() {
  local file_path
  file_path=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
  [ -z "$file_path" ] && allow

  case "$file_path" in
    */profile/config.yaml)
      local old_str required_agent
      old_str=$(echo "$INPUT" | jq -r '.tool_input.old_string // .tool_input.content // empty')
      required_agent=$(lookup_config_owner "$file_path" "$old_str")
      if [ -n "$required_agent" ]; then
        check_auth "$required_agent" && allow
        deny "config.yaml edit touches fields owned by: $required_agent. Authenticate as one of them."
      fi
      deny "config.yaml edit requires field-owner authentication."
      ;;
  esac

  local rel_path owner
  if rel_path=$(runtime_relative_path "$file_path"); then
    owner=$(lookup_runtime_owner "$rel_path")
    if [ -n "$owner" ]; then
      check_auth "$owner" && allow
      deny "This runtime-managed path is owned by $owner. Authenticate as $owner before editing it."
    fi
  elif rel_path=$(repo_relative_path "$file_path"); then
    owner=$(lookup_runtime_owner "$rel_path")
    if [ -n "$owner" ]; then
      check_auth "$owner" && allow
      deny "This repo path is owned by $owner. Authenticate as $owner before editing it."
    fi
  fi

  case "$file_path" in
    */dashboards/*.json|*/grafana*)
      check_auth sauron && allow
      deny "Dashboard edits require sauron authentication. Use /authenticate as sauron."
      ;;
  esac

  allow
}

guard_bash() {
  local cmd
  cmd=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
  [ -z "$cmd" ] && allow

  case "$cmd" in
    *git\ push*|*git\ \ push*)
      local push_cmd branch repo_root git_c_dir cd_dir
      push_cmd=$(echo "$cmd" | grep -oE 'git\s+push[^&;]*' | head -1)
      [ -z "$push_cmd" ] && allow

      branch=$(echo "$push_cmd" | grep -oE 'origin\s+(\S+)' | awk '{print $2}')
      branch=$(echo "$branch" | sed 's/.*://')
      if [ -z "$branch" ]; then
        git_c_dir=$(echo "$cmd" | grep -oE 'git\s+-C\s+(\S+)' | awk '{print $NF}')
        git_c_dir="${git_c_dir/#\~/$HOME}"
        if [ -n "$git_c_dir" ]; then
          branch=$(git -C "$git_c_dir" branch --show-current 2>/dev/null || echo "unknown")
        else
          branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        fi
      fi

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
          [ -n "$repo_root" ] && [ -d "$repo_root/.integrate-lock" ] && allow
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

  case "$cmd" in
    *kubectl*)
      if echo "$cmd" | grep -qE 'kubectl\s+(apply|create|delete|patch|replace|scale|rollout|drain|cordon|uncordon|taint|label|annotate)'; then
        if echo "$cmd" | grep -qE 'deploy(ment)?[/ ]workstation|kubectl\s+drain|kubectl\s+cordon'; then
          deny "Blocked: workstation deployment self-modification and node drain are never allowed from inside the pod."
        fi
        check_auth deployer && allow
        deny "kubectl write operations require deployer authentication. Use /infra."
      fi
      ;;
  esac

  if echo "$cmd" | grep -qE ':(30300|3000)/api/(dashboards|datasources|provisioning|admin|annotations)|grafana_admin'; then
    check_auth sauron && allow
    deny "Grafana operations require sauron authentication. Use /authenticate as sauron."
  fi

  allow
}

guard_grafana_mcp() {
  check_auth sauron && allow
  deny "Grafana MCP requires sauron authentication. Use /authenticate as sauron."
}

case "$TOOL" in
  Write|Edit)     guard_write ;;
  Bash)           guard_bash ;;
  mcp__grafana*)  guard_grafana_mcp ;;
  *)              allow ;;
esac
