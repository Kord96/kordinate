#!/bin/bash
# setup-agent-dir.sh <agent-name>
#
# Creates /kord/agents/<name>/ with:
#   CLAUDE.md         — generated @ imports (identity + shared + global memory)
#   identity.md       — converted from IDENTITY.md (Claude-agnostic)
#   .claude/settings.json — hooks template
#   memory/global/    — seeded from source if empty
#   memory/projects/  — empty, populated by curators per-project
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

mkdir -p "$DST/.claude" "$DST/memory/global" "$DST/memory/projects" "$DST/skills"

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

# ─── memory/global/ — seed from source (recursive, don't overwrite curator's work) ───

MEMORY_SRC="$SRC/agents/$AGENT/memory"
if [ -d "$MEMORY_SRC" ]; then
  # Copy entire memory tree into global/, preserving subdirectories (e.g., concepts/)
  # Use cp -rn (no-clobber) to avoid overwriting curator's merged files
  cp -rn "$MEMORY_SRC/." "$DST/memory/global/" 2>/dev/null || true
  # Remove any nested dynamic/pending dirs that shouldn't be in global
  rm -rf "$DST/memory/global/dynamic" "$DST/memory/global/pending" 2>/dev/null || true
  log "seeded memory/global/ from $MEMORY_SRC (recursive)"
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

# ─── CLAUDE.md — generate @ imports (global memory only) ───

{
  echo "@identity.md"

  # Shared files
  for f in "$DST/shared/"*.md; do
    [ -f "$f" ] || continue
    echo "@shared/$(basename "$f")"
  done

  # Global memory files
  for f in "$DST/memory/global/"*.md; do
    [ -f "$f" ] || continue
    base=$(basename "$f")
    echo "@memory/global/$base"
  done
} > "$DST/CLAUDE.md"

log "generated CLAUDE.md with $(wc -l < "$DST/CLAUDE.md") imports"
log "done: $DST"
