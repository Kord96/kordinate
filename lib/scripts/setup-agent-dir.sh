#!/bin/bash
# setup-agent-dir.sh <agent-name>
#
# Init container script — validates that the PVC layout exists for this agent.
# The PVC init job owns directory creation; agent startup should not reshape it.
# The deploy-runtime.sh script handles seeding from repo → runtime.
#
# Verifies:
#   /kord/<name>/
#     memory/
#     tmp/
#   /kord/shared/memory/

set -euo pipefail

AGENT="${1:?Usage: setup-agent-dir.sh <agent-name>}"
DST="/kord/$AGENT"

log() { echo "[setup-agent-dir] $*"; }

[ -d "$DST/memory" ] || { log "missing $DST/memory"; exit 1; }
[ -d "$DST/tmp" ] || { log "missing $DST/tmp"; exit 1; }
[ -d "/kord/shared/memory" ] || { log "missing /kord/shared/memory"; exit 1; }

log "directory structure ready: $DST"
