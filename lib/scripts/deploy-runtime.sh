#!/bin/bash
# deploy-runtime.sh [agent-name|all]
#
# Copies from repo → runtime:
#   repo/agents/<name>/memory/   → /kord/agents/<name>/memory/global/ (recursive, no-clobber)
#   repo/agents/<name>/IDENTITY.md → /kord/agents/<name>/identity.md (strip frontmatter)
#   repo/agents/<name>/skills/   → /kord/agents/<name>/skills/ (symlinks to repo)
#   repo/shared/                 → /kord/team/ (copy, overwrite)
#
# If "all" is passed, deploys for all agents. Otherwise just the named agent.
# Does NOT create directory structure — that's setup-agent-dir.sh's job.

set -euo pipefail

REPO="${KORDINATE_HOME:-/data/repos/kordinate}"
RUNTIME="/kord"

log() { echo "[deploy-runtime] $*"; }

deploy_agent() {
  local AGENT="$1"
  local SRC="$REPO/agents/$AGENT"
  local DST="$RUNTIME/agents/$AGENT"

  if [ ! -d "$SRC" ]; then
    log "WARN: no source dir at $SRC"
    return
  fi

  log "deploying $AGENT (src=$SRC dst=$DST)..."

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

  # Extract model
  local MODEL="sonnet"
  if [ -f "$SRC/IDENTITY.md" ]; then
    MODEL=$(sed -n 's/^model: *//p' "$SRC/IDENTITY.md" | head -1)
    [ -z "$MODEL" ] && MODEL="sonnet"
  fi
  echo "$MODEL" > "$DST/.model"
  log "  model: $MODEL"

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
| warden | Security validation, output contracts | haiku |

## Delegation

POST to the job router:
```
curl -s http://job-router:3100/api/delegate \
  -H "Content-Type: application/json" \
  -d '{"agent":"<name>","prompt":"<what you need>","project":"<optional>"}'
```
TEAM
    log "team/memory/global/team.md generated"
  fi
}

# Main
TARGET="${1:-all}"

log "repo: $REPO"
log "runtime: $RUNTIME"

deploy_team

if [ "$TARGET" = "all" ]; then
  for agent_dir in "$REPO/agents"/*/; do
    [ -d "$agent_dir" ] || continue
    agent=$(basename "$agent_dir")
    deploy_agent "$agent"
  done
else
  deploy_agent "$TARGET"
fi

log "deployment complete"
