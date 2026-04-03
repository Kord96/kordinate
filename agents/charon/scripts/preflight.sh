#!/bin/bash
# Charon preflight — deterministic skip for /survey when cluster state unchanged.
# Receives job JSON on stdin. Outputs "SKIP: <message>" to skip, or nothing to proceed.

set -euo pipefail

JOB=$(cat)
PROMPT=$(echo "$JOB" | python3 -c "import json,sys; print(json.load(sys.stdin).get('prompt',''))")

# Only gate survey jobs
echo "$PROMPT" | grep -qi "survey" || exit 0

# Force full if --full in prompt
echo "$PROMPT" | grep -qi "\-\-full" && exit 0

ATLAS="${AGENT_PROJECT_DIR}/memory/global/infra-atlas.json"

# No atlas yet — proceed
[ -f "$ATLAS" ] || exit 0

# Get stored hash
PREV_HASH=$(python3 -c "import json; print(json.load(open('$ATLAS')).get('metadata',{}).get('cluster_hash',''))" 2>/dev/null)
[ -z "$PREV_HASH" ] && exit 0

# Compute current cluster state hash
CURRENT_HASH=$(kubectl get nodes,deployments,statefulsets,services,pvcs --all-namespaces -o json 2>/dev/null | sha256sum | cut -d' ' -f1)
[ -z "$CURRENT_HASH" ] && exit 0

if [ "$PREV_HASH" = "$CURRENT_HASH" ]; then
  GENERATED=$(python3 -c "import json; print(json.load(open('$ATLAS')).get('metadata',{}).get('generated','unknown'))" 2>/dev/null)
  echo "SKIP: Infrastructure atlas is current (hash ${PREV_HASH:0:12}..., generated $GENERATED). No cluster state changes."
fi
