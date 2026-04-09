#!/bin/bash
# setup-agent-dir.sh <agent-name>
#
# Init container script — ensures the minimal PVC layout exists for this agent.
# Klaude owns the runtime process; Kordinate prepares the baseline runtime dirs.
# The deploy-runtime.sh script handles seeding from repo → runtime.
#
# Ensures:
#   /kord/<name>/
#     memory/
#     tmp/
#   /kord/shared/memory/

set -euo pipefail

AGENT="${1:?Usage: setup-agent-dir.sh <agent-name>}"
DST="/kord/$AGENT"

log() { echo "[setup-agent-dir] $*"; }

mkdir -p "$DST/memory" "$DST/tmp" "/kord/shared/memory"

log "directory structure ready: $DST"
