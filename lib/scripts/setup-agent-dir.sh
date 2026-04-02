#!/bin/bash
# setup-agent-dir.sh <agent-name>
#
# Init container script — ensures the agent runtime directory structure exists.
# Does NOT read from the repo. The deploy-runtime.sh script handles seeding
# from repo → runtime.
#
# Creates:
#   /kord/agents/<name>/
#     .claude/
#     memory/global/
#     memory/projects/
#     skills/
#   /kord/team/
#     memory/global/

set -euo pipefail

AGENT="${1:?Usage: setup-agent-dir.sh <agent-name>}"
DST="/kord/agents/$AGENT"

log() { echo "[setup-agent-dir] $*"; }

mkdir -p \
  "$DST/.claude" \
  "$DST/memory/global" \
  "$DST/memory/projects" \
  "$DST/skills" \
  "/kord/team/memory/global"

log "directory structure ready: $DST"
