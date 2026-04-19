#!/bin/bash
# deploy-runtime.sh [source-agent|all] [destination-agent]
#
# Kordinate-side runtime seeding only. Klaude owns the harness/runtime behavior.
# This script prepares runtime files and metadata that the Klaude daemon reads.
#
# Copies from repo → runtime:
#   repo/agents/<name>/memory/     → <runtime>/<name>/memory/global/ (recursive, no-clobber)
#   repo/agents/<name>/IDENTITY.md → <runtime>/<name>/identity.md (strip frontmatter)
#   repo/agents/<name>/skills/     → <runtime>/<name>/skills/ (symlinks to repo)
#   repo/shared/skills/ + repo/agents/<name>/skills/
#                                  → <runtime>/<name>/.claude/skills/ (symlinks for Claude-family runtimes)
#   repo/shared/memory/            → /kord/shared/memory/ (copy, no-clobber)
#
# If "all" is passed, deploys for all agents. Otherwise deploys from the source
# agent directory, optionally into a different destination agent name.
# Does NOT create the PVC layout — bootstrap owns that.
# Does NOT implement Kafka request/reply semantics — Klaude does.

set -euo pipefail

REPO="${KORDINATE_HOME:-/app}"
RUNTIME="${KORD_RUNTIME:-/kord/agents}"
KORD_ROOT="${KORD_ROOT:-/kord}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() { echo "[deploy-runtime] $*"; }

normalize_backend_name() {
  local profile="$1"
  local model="$2"
  local base_url="$3"
  local backend_name="$4"

  if [ -n "$backend_name" ]; then
    echo "$backend_name"
    return
  fi

  case "$profile" in
    anthropic) echo "anthropic" ;;
    gemini) echo "gemini" ;;
    ollama) echo "ollama" ;;
    openai)
      case "$base_url" in
        *deepseek*) echo "deepseek" ;;
        *fireworks*) echo "fireworks" ;;
        *chatgpt.com*) echo "codex" ;;
        *)
          if [[ "$model" == codex* ]]; then
            echo "codex"
          else
            echo "openai-compatible"
          fi
          ;;
      esac
      ;;
    *) echo "$profile" ;;
  esac
}

normalize_api_key_env() {
  local profile="$1"
  local base_url="$2"
  local backend_name="$3"
  local api_key_env="$4"

  if [ -n "$api_key_env" ]; then
    echo "$api_key_env"
    return
  fi

  case "$profile" in
    anthropic) echo "ANTHROPIC_API_KEY" ;;
    gemini) echo "GEMINI_API_KEY" ;;
    ollama) echo "" ;;
    openai)
      case "$backend_name:$base_url" in
        deepseek:*|*:https://api.deepseek.com*) echo "DEEPSEEK_API_KEY" ;;
        fireworks:*|*:https://api.fireworks.ai/*) echo "FIREWORKS_API_KEY" ;;
        codex:*|*:https://chatgpt.com/*) echo "OPENAI_API_KEY" ;;
        *) echo "OPENAI_API_KEY" ;;
      esac
      ;;
    *) echo "" ;;
  esac
}

deploy_agent() {
  local SOURCE_AGENT="$1"
  local DEST_AGENT="$2"
  local SRC="$REPO/agents/$SOURCE_AGENT"
  local DST="$RUNTIME/$DEST_AGENT"
  local SHARED_ALFRED_ROOT="$KORD_ROOT/alfred"
  if [ ! -d "$SRC" ]; then
    log "WARN: no source dir at $SRC"
    return
  fi

  log "deploying source=$SOURCE_AGENT dest=$DEST_AGENT (src=$SRC dst=$DST)..."

  # Ensure destination directory exists
  mkdir -p "$DST"

  # Shared specialization alias for deterministic compatibility paths such as
  # /kord/agents/augur/... used by some model backends during exploration.
  if [ "$SOURCE_AGENT" != "$DEST_AGENT" ]; then
    ln -sfn "$SRC" "$RUNTIME/$SOURCE_AGENT"
  fi

  # Memory: recursive copy, don't overwrite scribe's merged files
  if [ -d "$SRC/memory" ]; then
    mkdir -p "$DST/memory/global"
    local src_count=$(find "$SRC/memory" -type f | wc -l)
    log "  memory source: $SRC/memory ($src_count files)"
    # cp -rn requires GNU coreutils (BusyBox cp lacks -n / --no-clobber).
    # Fall back to a find-based copy if cp -n is not supported.
    if cp --help 2>&1 | grep -q 'no-clobber\|-n'; then
      cp -rn "$SRC/memory/." "$DST/memory/global/"
    else
      log "  WARN: cp -n not available, using find-based no-clobber copy"
      (cd "$SRC/memory" && find . -type f) | while read -r f; do
        if [ ! -e "$DST/memory/global/$f" ]; then
          mkdir -p "$(dirname "$DST/memory/global/$f")"
          cp "$SRC/memory/$f" "$DST/memory/global/$f"
        fi
      done
    fi
    rm -rf "$DST/memory/global/dynamic" "$DST/memory/global/pending" 2>/dev/null || true
    local dst_count=$(find "$DST/memory/global" -type f | wc -l)
    log "  memory/global/ seeded ($dst_count files)"
  else
    log "  WARN: no memory dir at $SRC/memory"
  fi

  # Identity: strip frontmatter
  if [ -f "$SRC/IDENTITY.md" ]; then
    sed '/^---$/,/^---$/d' "$SRC/IDENTITY.md" > "$DST/identity.md"
    log "  identity.md created"
  fi

  if [ "$SOURCE_AGENT" = "alfred" ]; then
    mkdir -p "$SHARED_ALFRED_ROOT/pass" "$SHARED_ALFRED_ROOT/gnupg" "$SHARED_ALFRED_ROOT/tmp"
    chmod 700 "$SHARED_ALFRED_ROOT/pass" "$SHARED_ALFRED_ROOT/gnupg" 2>/dev/null || true
    chmod -R u+rwX,g+rwX "$SHARED_ALFRED_ROOT/tmp"

    ln -sfn "$SHARED_ALFRED_ROOT/pass" "$DST/.password-store"
    ln -sfn "$SHARED_ALFRED_ROOT/gnupg" "$DST/.gnupg"

    local GPG_KEY_ID=""
    GPG_KEY_ID="$(GNUPGHOME="$SHARED_ALFRED_ROOT/gnupg" gpg --batch --list-secret-keys --with-colons 2>/dev/null | awk -F: '/^sec:/ {print $5; exit}')"
    if [ -z "$GPG_KEY_ID" ]; then
      GNUPGHOME="$SHARED_ALFRED_ROOT/gnupg" gpg --batch --pinentry-mode loopback --passphrase '' \
        --quick-gen-key "Alfred Kord Cluster <alfred@kord.local>" default default never >/dev/null
      GPG_KEY_ID="$(GNUPGHOME="$SHARED_ALFRED_ROOT/gnupg" gpg --batch --list-secret-keys --with-colons 2>/dev/null | awk -F: '/^sec:/ {print $5; exit}')"
    fi

    if [ -n "$GPG_KEY_ID" ] && [ ! -f "$SHARED_ALFRED_ROOT/pass/.gpg-id" ]; then
      PASSWORD_STORE_DIR="$SHARED_ALFRED_ROOT/pass" GNUPGHOME="$SHARED_ALFRED_ROOT/gnupg" pass init "$GPG_KEY_ID" >/dev/null
    fi

    chown -R 1000:1000 "$SHARED_ALFRED_ROOT"
    chmod 700 "$SHARED_ALFRED_ROOT/pass" "$SHARED_ALFRED_ROOT/gnupg" 2>/dev/null || true
    log "  Alfred shared pass/GPG runtime prepared"
  fi

  # Extract profile + backend configuration
  local PROFILE=""
  local MODEL="sonnet"
  local PROVIDER="anthropic"
  local BASE_URL=""
  local API_KEY_REF=""
  local API_KEY_ENV=""
  local BACKEND_NAME=""
  local BACKEND_STRATEGY="first"
  local BACKENDS_FILE="$SRC/BACKENDS.json"

  if [ -f "$SRC/IDENTITY.md" ]; then
    PROFILE=$(sed -n 's/^profile: *//p' "$SRC/IDENTITY.md" | head -1)
    MODEL=$(sed -n 's/^model: *//p' "$SRC/IDENTITY.md" | head -1)
    [ -z "$MODEL" ] && MODEL="sonnet"
    BASE_URL=$(sed -n 's/^base_url: *//p' "$SRC/IDENTITY.md" | head -1)
    API_KEY_REF=$(sed -n 's/^api_key_ref: *//p' "$SRC/IDENTITY.md" | head -1)
    API_KEY_ENV=$(sed -n 's/^api_key_env: *//p' "$SRC/IDENTITY.md" | head -1)
    BACKEND_NAME=$(sed -n 's/^backend_name: *//p' "$SRC/IDENTITY.md" | head -1)
    BACKEND_STRATEGY=$(sed -n 's/^backend_strategy: *//p' "$SRC/IDENTITY.md" | head -1)
    [ -z "$BACKEND_STRATEGY" ] && BACKEND_STRATEGY="first"
  fi

  # Backward compatibility: map legacy model/provider specs into the new profile model
  if [ -z "$PROFILE" ]; then
    PROVIDER="anthropic"
    if [[ "$MODEL" == *":"* ]]; then
      PROVIDER="${MODEL%%:*}"
      MODEL="${MODEL#*:}"
    fi

    case "$PROVIDER" in
      claude|anthropic)
        PROFILE="anthropic"
        ;;
      deepseek)
        PROFILE="openai"
        BASE_URL="${BASE_URL:-https://api.deepseek.com/v1}"
        BACKEND_NAME="${BACKEND_NAME:-deepseek}"
        ;;
      fireworks)
        PROFILE="openai"
        BASE_URL="${BASE_URL:-https://api.fireworks.ai/inference/v1}"
        BACKEND_NAME="${BACKEND_NAME:-fireworks}"
        ;;
      openai)
        PROFILE="openai"
        ;;
      gemini)
        PROFILE="gemini"
        ;;
      ollama)
        PROFILE="ollama"
        BASE_URL="${BASE_URL:-http://localhost:11434/v1}"
        BACKEND_NAME="${BACKEND_NAME:-ollama}"
        ;;
      *)
        PROFILE="anthropic"
        ;;
    esac
  fi

  case "$PROFILE" in
    claude)
      PROFILE="anthropic"
      ;;
  esac

  BACKEND_NAME=$(normalize_backend_name "$PROFILE" "$MODEL" "$BASE_URL" "$BACKEND_NAME")
  API_KEY_ENV=$(normalize_api_key_env "$PROFILE" "$BASE_URL" "$BACKEND_NAME" "$API_KEY_ENV")
  PROVIDER="$PROFILE"

  if [ "$PROFILE" = "anthropic" ] && [ -z "$BASE_URL" ]; then
    BASE_URL=""
  elif [ "$PROFILE" = "ollama" ] && [ -z "$BASE_URL" ]; then
    BASE_URL="http://localhost:11434/v1"
  fi

  if [ -f "$BACKENDS_FILE" ]; then
    python3 - "$BACKENDS_FILE" "$DST/.openclaude-backends.json" "$BACKEND_STRATEGY" <<'PY'
import json, sys
src, dst, fallback_selection = sys.argv[1:4]
with open(src, 'r', encoding='utf-8') as f:
    data = json.load(f)
if isinstance(data, list):
    data = {'backends': data}
if not isinstance(data, dict) or not isinstance(data.get('backends'), list) or not data['backends']:
    raise SystemExit('BACKENDS.json must contain a non-empty "backends" list')
data.setdefault('version', 2)
data.setdefault('selection', fallback_selection or 'first')
with open(dst, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
PY
  else
    python3 - "$DST/.openclaude-backends.json" "$PROFILE" "$PROVIDER" "$BACKEND_NAME" "$MODEL" "$BASE_URL" "$API_KEY_ENV" "$API_KEY_REF" "$BACKEND_STRATEGY" <<'PY'
import json, sys
(dst, profile, provider, backend_name, model, base_url, api_key_env, api_key_ref, selection) = sys.argv[1:10]
base_url = base_url or None
api_key_env = api_key_env or None
api_key_ref = api_key_ref or None
payload = {
    'version': 2,
    'selection': selection or 'first',
    'backends': [{
        'name': backend_name,
        'profile': profile,
        'provider': provider,
        'model': model,
        'base_url': base_url,
        'api_key_env': api_key_env,
        'api_key_ref': api_key_ref,
    }],
}
with open(dst, 'w', encoding='utf-8') as f:
    json.dump(payload, f, indent=2)
    f.write('\n')
PY
  fi

  python3 - "$DST/.openclaude-backends.json" "$DST/.openclaude-profile.json" <<'PY'
import json, sys
src, dst = sys.argv[1:3]
with open(src, 'r', encoding='utf-8') as f:
    pool = json.load(f)
backend = dict(pool['backends'][0])
profile = {
    'version': pool.get('version', 2),
    'selection': pool.get('selection', 'first'),
    'backend_name': backend.get('name'),
    'profile': backend.get('profile'),
    'provider': backend.get('provider') or backend.get('profile'),
    'model': backend.get('model'),
    'base_url': backend.get('base_url'),
    'api_key_env': backend.get('api_key_env'),
    'api_key_ref': backend.get('api_key_ref'),
    'env_passthrough': backend.get('env_passthrough', []),
    'extra_env': backend.get('extra_env', {}),
    'createdAt': __import__('datetime').datetime.utcnow().replace(microsecond=0).isoformat() + 'Z',
}
with open(dst, 'w', encoding='utf-8') as f:
    json.dump(profile, f, indent=2)
    f.write('\n')
PY

  local LEGACY_PROVIDER
  local LEGACY_MODEL
  local LEGACY_SPEC
  read -r LEGACY_PROVIDER LEGACY_MODEL LEGACY_SPEC <<EOF
$(python3 - "$DST/.openclaude-profile.json" <<'PY'
import json, sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    profile = json.load(f)
provider = profile.get('provider') or profile.get('profile') or 'anthropic'
model = profile.get('model') or ''
print(provider, model, f"{provider}:{model}")
PY
)
EOF

  echo "$LEGACY_MODEL" > "$DST/.model"
  echo "$LEGACY_PROVIDER" > "$DST/.provider"
  echo "$LEGACY_SPEC" > "$DST/.model-spec"

  log "  profile: $PROFILE"
  log "  provider: $PROVIDER"
  log "  backend: $BACKEND_NAME"
  log "  model: $MODEL"
  log "  base_url: ${BASE_URL:-none}"
  log "  api_key_env: ${API_KEY_ENV:-none}"
  log "  api_key_ref: ${API_KEY_REF:-none}"
  log "  backend_strategy: ${BACKEND_STRATEGY:-first}"

  # Skills: symlink to repo (read from data PVC)
  if [ -d "$SRC/skills" ]; then
    mkdir -p "$DST/skills"
    for skill_dir in "$SRC/skills"/*/; do
      [ -d "$skill_dir" ] || continue
      local skill_name=$(basename "$skill_dir")
      ln -sfn "$skill_dir" "$DST/skills/$skill_name"
      log "  linked skills/$skill_name"
    done
  fi

  # Claude-family runtimes discover skills from $HOME/.claude/skills.
  # Mirror both shared skills and agent-local skills into the runtime home so
  # runtime-native Skill tool invocation can resolve the same source-of-truth
  # SKILL.md files that the repo owns.
  local CLAUDE_SKILLS_DIR="$DST/.claude/skills"
  mkdir -p "$CLAUDE_SKILLS_DIR"
  if [ -d "$REPO/shared/skills" ]; then
    for skill_dir in "$REPO/shared/skills"/*/; do
      [ -d "$skill_dir" ] || continue
      local skill_name=$(basename "$skill_dir")
      ln -sfn "$skill_dir" "$CLAUDE_SKILLS_DIR/$skill_name"
      log "  linked .claude/skills/$skill_name (shared)"
    done
  fi
  if [ -d "$SRC/skills" ]; then
    for skill_dir in "$SRC/skills"/*/; do
      [ -d "$skill_dir" ] || continue
      local skill_name=$(basename "$skill_dir")
      ln -sfn "$skill_dir" "$CLAUDE_SKILLS_DIR/$skill_name"
      log "  linked .claude/skills/$skill_name (agent)"
    done
  fi

  # Preflight script (if agent provides one)
  if [ -f "$SRC/scripts/preflight.sh" ]; then
    cp "$SRC/scripts/preflight.sh" "$DST/preflight.sh"
    chmod +x "$DST/preflight.sh"
    log "  preflight.sh installed"
  fi

  local AGENT_BUNDLE_NAME="AGENT.md"
  local AGENT_BUNDLE_SRC="$SRC/INDEX.yaml"
  local AGENT_BUNDLE_DST="$DST/$AGENT_BUNDLE_NAME"

  if [ -f "$AGENT_BUNDLE_SRC" ]; then
    python3 "$SCRIPT_DIR/generate-agent-bundle.py" "$SRC" "$AGENT_BUNDLE_DST"
    log "  $AGENT_BUNDLE_NAME generated"
  fi

  # Generate CLAUDE.md as a compatibility shim for runtimes that still look for it.
  # AGENT.md is the canonical seeded-context bundle; CLAUDE.md should only reference it.
  {
    if [ -f "$AGENT_BUNDLE_DST" ]; then
      echo "@$AGENT_BUNDLE_NAME"
    else
      echo "@identity.md"
    fi
  } > "$DST/CLAUDE.md"
  log "  CLAUDE.md generated"

  # Write a separate skills index for human/runtime discoverability without mutating CLAUDE.md
  {
    echo "# Skills"
    echo ""
    if [ -d "$DST/skills" ]; then
      for skill_dir in "$DST/skills"/*/; do
        [ -d "$skill_dir" ] || continue
        local sname=$(basename "$skill_dir")
        if [ -f "$skill_dir/SKILL.md" ]; then
          local sdesc=$(sed -n 's/^description: *//p' "$skill_dir/SKILL.md" | head -1 | sed 's/^> *//')
          echo "- /$sname — $sdesc"
        else
          echo "- /$sname"
        fi
      done
    fi
  } > "$DST/SKILLS.md"
  log "  SKILLS.md generated"

  chown -R 1000:1000 "$DST"
  chmod -R u+rwX,g+rwX "$DST"

  log "  done"
}

deploy_team() {
  local SRC="$REPO/shared"
  local DST="$RUNTIME/team/memory/global"

  mkdir -p "$DST"

  if [ -d "$SRC" ]; then
    log "team source: $SRC"
    for f in "$SRC/"*.md; do
      [ -f "$f" ] || continue
      local base=$(basename "$f")
      # Strip frontmatter
      sed '/^---$/,/^---$/d' "$f" > "$DST/$base"
      log "team/memory/global/$base deployed"
    done
  else
    log "WARN: no shared dir at $SRC"
  fi

  # Generate team.md if missing
  if [ ! -f "$DST/team.md" ]; then
    cat > "$DST/team.md" << 'TEAM'
# Team

| Agent | Domain | Model |
|-------|--------|-------|
| augur | Architecture analysis, pattern detection | opus |
| charon | Infrastructure, deployments, cluster ops | sonnet |
| sauron | Monitoring, observability, metrics | sonnet |
| alfred | Config, credentials, overlays | haiku |

## Delegation

Publish a request to the target Kafka topic `agent.<name>`.
Example request:
```
{"prompt":"<what you need>","timeout_ms":1500000,"reflect":true,"reply_to":"agent.master-workstation"}
```

Replies are published by Klaude to `reply_to` and use:
```
{"status":"success|error|timeout|cancelled","output":"<text>","reflection":{"project":"<optional>","general":"<optional>"},"errors":["<optional>"]}
```
TEAM
    log "team/memory/global/team.md generated"
  fi

  chown -R 1000:1000 "$DST"
  chmod -R u+rwX,g+rwX "$DST"
}

# Main
SOURCE_TARGET="${1:-all}"
DEST_TARGET="${2:-}"

log "repo: $REPO"
log "runtime: $RUNTIME"

deploy_team

if [ "$SOURCE_TARGET" = "all" ]; then
  for agent_dir in "$REPO/agents"/*/; do
    [ -d "$agent_dir" ] || continue
    agent=$(basename "$agent_dir")
    deploy_agent "$agent" "$agent"
  done
else
  if [ -n "$DEST_TARGET" ]; then
    deploy_agent "$SOURCE_TARGET" "$DEST_TARGET"
  else
    deploy_agent "$SOURCE_TARGET" "$SOURCE_TARGET"
  fi
fi

log "deployment complete"
