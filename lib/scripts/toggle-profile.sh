#!/bin/bash
set -euo pipefail

# Manage per-agent OpenClaude backend pools under /kord/agents/<agent>/
if [ $# -lt 2 ]; then
  echo "Usage: $0 <show|select|list> <agent> [backend-name]"
  exit 1
fi

COMMAND="$1"
AGENT="$2"
BACKEND_NAME="${3:-}"
RUNTIME_ROOT="${KORD_RUNTIME:-/kord}"
AGENT_DIR="$RUNTIME_ROOT/agents/$AGENT"
POOL_FILE="$AGENT_DIR/.openclaude-backends.json"
PROFILE_FILE="$AGENT_DIR/.openclaude-profile.json"

show_current() {
  if [ -f "$PROFILE_FILE" ]; then
    python3 -m json.tool "$PROFILE_FILE"
  else
    echo "No active profile for agent $AGENT"
  fi
}

list_backends() {
  if [ ! -f "$POOL_FILE" ]; then
    echo "No backend pool found for agent $AGENT"
    return 1
  fi
  python3 - "$POOL_FILE" <<'PY'
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    pool = json.load(f)
for backend in pool.get('backends', []):
    print(f"{backend.get('name')}\t{backend.get('profile')}\t{backend.get('model')}")
PY
}

select_backend() {
  if [ -z "$BACKEND_NAME" ]; then
    echo "Usage: $0 select <agent> <backend-name>"
    return 1
  fi
  if [ ! -f "$POOL_FILE" ]; then
    echo "No backend pool found for agent $AGENT"
    return 1
  fi
  python3 - "$POOL_FILE" "$PROFILE_FILE" "$BACKEND_NAME" <<'PY'
import json, sys, datetime
pool_file, profile_file, backend_name = sys.argv[1:4]
with open(pool_file, 'r', encoding='utf-8') as f:
    pool = json.load(f)
backend = next((b for b in pool.get('backends', []) if b.get('name') == backend_name), None)
if not backend:
    raise SystemExit(f"Backend not found: {backend_name}")
profile = {
    'version': pool.get('version', 2),
    'selection': 'manual',
    'backend_name': backend.get('name'),
    'profile': backend.get('profile'),
    'provider': backend.get('provider') or backend.get('profile'),
    'model': backend.get('model'),
    'base_url': backend.get('base_url'),
    'api_key_env': backend.get('api_key_env'),
    'api_key_ref': backend.get('api_key_ref'),
    'env_passthrough': backend.get('env_passthrough', []),
    'extra_env': backend.get('extra_env', {}),
    'createdAt': datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z',
}
with open(profile_file, 'w', encoding='utf-8') as f:
    json.dump(profile, f, indent=2)
    f.write('\n')
print(f"Selected backend {backend_name} for agent {profile.get('backend_name')}")
PY
}

case "$COMMAND" in
  show)
    show_current
    ;;
  list)
    list_backends
    ;;
  select)
    select_backend
    ;;
  *)
    echo "Usage: $0 <show|select|list> <agent> [backend-name]"
    exit 1
    ;;
esac
