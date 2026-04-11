#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <registry-host> [--verify-local]"
  exit 1
fi

REGISTRY="$1"
VERIFY_LOCAL="${2:-}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

build_and_push() {
  local name="$1"
  local dockerfile="$2"
  docker build \
    --build-arg REGISTRY="$REGISTRY" \
    -f "$dockerfile" \
    -t "$REGISTRY/$name:latest" \
    "$REPO_ROOT"
  if [[ "$VERIFY_LOCAL" == "--verify-local" ]]; then
    "$REPO_ROOT/lib/scripts/verify-agent-image.sh" "$REGISTRY/$name:latest"
  fi
  docker push "$REGISTRY/$name:latest"
}

# Bootstrap set from docs/bootstrap-image-policy.md.
build_and_push "agent-base" "$REPO_ROOT/agents/charon/skills/bootstrap/images/agent-base/Dockerfile"
build_and_push "agent-charon" "$REPO_ROOT/agents/charon/skills/bootstrap/images/charon/Dockerfile"
build_and_push "agent-augur" "$REPO_ROOT/agents/charon/skills/bootstrap/images/augur/Dockerfile"
build_and_push "agent-alfred" "$REPO_ROOT/agents/charon/skills/bootstrap/images/alfred/Dockerfile"
build_and_push "agent-sauron" "$REPO_ROOT/agents/charon/skills/bootstrap/images/sauron/Dockerfile"
