#!/bin/bash
# Augur preflight — deterministic skip for /analyze when atlas is current.
# Receives job JSON on stdin. Outputs "SKIP: <message>" to skip, or nothing to proceed.

set -euo pipefail

JOB=$(cat)
PROJECT=$(echo "$JOB" | python3 -c "import json,sys; print(json.load(sys.stdin).get('project',''))")
PROMPT=$(echo "$JOB" | python3 -c "import json,sys; print(json.load(sys.stdin).get('prompt',''))")

# Only gate analyze jobs
echo "$PROMPT" | grep -qi "analyze" || exit 0

# --full or "full analysis" bypasses the skip
echo "$PROMPT" | grep -qi "\-\-full\|full analysis" && exit 0

# Need a project to check
[ -z "$PROJECT" ] && exit 0

PROJ_CODE="${PROJECTS_ROOT}/${PROJECT}"
ATLAS="${AGENT_PROJECT_DIR}/memory/projects/${PROJECT}/atlas.json"

# No atlas yet — proceed to Claude for full analysis
[ -f "$ATLAS" ] || exit 0

# No project code — proceed (daemon will clone)
[ -d "$PROJ_CODE" ] || exit 0

# Compare SHA
PREV_SHA=$(python3 -c "import json; print(json.load(open('$ATLAS')).get('metadata',{}).get('analyzed_at_sha',''))" 2>/dev/null)
[ -z "$PREV_SHA" ] && exit 0

HEAD_SHA=$(git -C "$PROJ_CODE" rev-parse HEAD 2>/dev/null)
[ -z "$HEAD_SHA" ] && exit 0

if [ "$PREV_SHA" = "$HEAD_SHA" ]; then
  echo "SKIP: Atlas is current at SHA ${HEAD_SHA}. No code changes since last analysis."
fi
