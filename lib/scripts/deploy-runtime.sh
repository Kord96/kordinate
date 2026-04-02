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
    log "WARN: no source for agent $AGENT"
    return
  fi

  log "deploying $AGENT..."

  # Memory: recursive copy, don't overwrite scribe's merged files
  if [ -d "$SRC/memory" ]; then
    mkdir -p "$DST/memory/global"
    cp -rn "$SRC/memory/." "$DST/memory/global/" 2>/dev/null || true
    rm -rf "$DST/memory/global/dynamic" "$DST/memory/global/pending" 2>/dev/null || true
    log "  memory/global/ seeded"
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
    for f in "$SRC/"*.md; do
      [ -f "$f" ] || continue
      local base=$(basename "$f")
      # Strip frontmatter
      sed '/^---$/,/^---$/d' "$f" > "$DST/$base"
      log "team/memory/global/$base deployed"
    done
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
