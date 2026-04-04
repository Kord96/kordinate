#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <registry-host>"
  exit 1
fi

REGISTRY="$1"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

build_and_push() {
  local name="$1"
  local dockerfile="$2"
  docker build -f "$dockerfile" -t "$REGISTRY/$name:latest" "$REPO_ROOT"
  docker push "$REGISTRY/$name:latest"
}

build_and_push "agent-base" "$REPO_ROOT/agents/charon/skills/bootstrap/images/agent-base/Dockerfile"
build_and_push "agent-charon" "$REPO_ROOT/agents/charon/skills/bootstrap/images/charon/Dockerfile"
build_and_push "agent-augur" "$REPO_ROOT/agents/charon/skills/bootstrap/images/augur/Dockerfile"
