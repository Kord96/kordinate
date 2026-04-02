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
#     memory/shared/
#     memory/projects/
#     memory/local-global/
#     skills/

set -euo pipefail

AGENT="${1:?Usage: setup-agent-dir.sh <agent-name>}"
DST="/kord/agents/$AGENT"

log() { echo "[setup-agent-dir] $*"; }

# Create directory structure
mkdir -p \
  "$DST/.claude" \
  "$DST/memory/global" \
  "$DST/memory/shared" \
  "$DST/memory/projects" \
  "$DST/memory/local-global" \
  "$DST/skills"

# Create team dir if it doesn't exist
mkdir -p /kord/team

log "directory structure ready: $DST"
