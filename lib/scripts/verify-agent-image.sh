#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <image-ref>"
  exit 1
fi

IMAGE="$1"

docker run --rm --entrypoint /bin/bash "$IMAGE" -lc '
set -euo pipefail
which klaude-daemon >/dev/null
test -f /app/shared/klaude-daemon/dist/index.js
test -x /app/lib/scripts/setup-agent-dir.sh
test -x /app/lib/scripts/deploy-runtime.sh
'

echo "verified: $IMAGE"
