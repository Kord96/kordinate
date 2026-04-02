#!/bin/bash
# setup-agent-dir.sh <agent-name>
#
# Creates /kord/agents/<name>/ with:
#   CLAUDE.md         — generated @ imports (Claude-specific glue)
#   identity.md       — converted from IDENTITY.md (Claude-agnostic)
#   .claude/settings.json — hooks template
#   memory/           — seeded from source if empty
#   skills/           — symlinks to source skill dirs
#   shared/           — symlink to /kord/agents/shared/
#
# Run as init container or manually to populate the shared PVC.

set -euo pipefail

AGENT="${1:?Usage: setup-agent-dir.sh <agent-name>}"
SRC="${KORDINATE_HOME:-/kord/kordinate}"
DST="/kord/agents/$AGENT"
SHARED="/kord/agents/shared"

log() { echo "[setup-agent-dir] $*"; }

# ─── Create shared directory if it doesn't exist ───

mkdir -p "$SHARED"

# Copy shared protocols from source (idempotent)
for proto in "$SRC/team/shared/"*.md; do
  [ -f "$proto" ] || continue
  base=$(basename "$proto")
  # Strip frontmatter from protocols
  sed '/^---$/,/^---$/d' "$proto" > "$SHARED/$base"
done

# Create team.md if it doesn't exist
if [ ! -f "$SHARED/team.md" ]; then
  cat > "$SHARED/team.md" << 'TEAM'
# Team

| Agent | Domain | Capabilities |
|-------|--------|-------------|
| augur | Architecture | Project analysis, pattern detection, debt assessment, API review |
| warden | Security | Output validation, secret scanning, content sanitization |
| charon | Infrastructure | Deployments, cluster ops, node management, rolling updates |
| sauron | Monitoring | Metrics, logs, dashboards, alert design, anomaly detection |
| scribe | Documentation | Documentation generation, health checks |
| alfred | Config | Credentials, overlays, environment preflight |

## Delegation

To request help from another agent:

```
curl -s http://job-router.master.svc.cluster.local:3100/api/delegate \
  -H "Content-Type: application/json" \
  -d '{"agent":"<name>","prompt":"<what you need>"}'
```

The response contains the agent's output. This is a synchronous call —
it blocks until the target agent completes the work.
TEAM
  log "created team.md"
fi

# ─── Create agent directory ───

mkdir -p "$DST/.claude" "$DST/memory" "$DST/skills"

# ─── identity.md — strip frontmatter from IDENTITY.md ───

IDENTITY_SRC="$SRC/agents/$AGENT/IDENTITY.md"
if [ -f "$IDENTITY_SRC" ]; then
  # Strip YAML frontmatter (everything between --- markers)
  sed '/^---$/,/^---$/d' "$IDENTITY_SRC" > "$DST/identity.md"
  log "created identity.md from IDENTITY.md"
else
  log "WARN: no IDENTITY.md found for $AGENT"
fi

# ─── .claude/settings.json — copy template ───

cp "$SRC/lib/templates/agent-settings.json" "$DST/.claude/settings.json"
log "created .claude/settings.json"

# ─── memory/ — seed from source if empty ───

MEMORY_SRC="$SRC/agents/$AGENT/memory"
if [ -d "$MEMORY_SRC" ]; then
  for f in "$MEMORY_SRC/"*.md; do
    [ -f "$f" ] || continue
    base=$(basename "$f")
    # Only seed if file doesn't exist (don't overwrite curator's work)
    if [ ! -f "$DST/memory/$base" ]; then
      cp "$f" "$DST/memory/$base"
      log "seeded memory/$base"
    fi
  done
fi

# ─── skills/ — symlink to source skill dirs ───

SKILLS_SRC="$SRC/agents/$AGENT/skills"
if [ -d "$SKILLS_SRC" ]; then
  for skill_dir in "$SKILLS_SRC"/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name=$(basename "$skill_dir")
    ln -sfn "$skill_dir" "$DST/skills/$skill_name"
    log "linked skills/$skill_name"
  done
fi

# ─── shared/ — symlink to shared directory ───

ln -sfn "$SHARED" "$DST/shared"
log "linked shared/"

# ─── CLAUDE.md — generate @ imports ───

{
  echo "@identity.md"

  # Shared files
  for f in "$DST/shared/"*.md; do
    [ -f "$f" ] || continue
    echo "@shared/$(basename "$f")"
  done

  # Memory files
  for f in "$DST/memory/"*.md; do
    [ -f "$f" ] || continue
    base=$(basename "$f")
    [ "$base" = "MEMORY.md" ] && continue  # skip index files
    echo "@memory/$base"
  done
} > "$DST/CLAUDE.md"

log "generated CLAUDE.md with $(wc -l < "$DST/CLAUDE.md") imports"
log "done: $DST"
