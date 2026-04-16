#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: build-agent-images.sh <registry-host> [options]

Options:
  --image <name>         Build only one image (repeatable).
  --tag <tag>            Push this explicit tag in addition to :latest.
  --verify-local         Run local image verification after each build.

Known images:
  agent-base
  agent-charon
  agent-augur
  agent-alfred
  agent-sauron
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

REGISTRY="$1"
shift
VERIFY_LOCAL=0
TAG=""
declare -a REQUESTED_IMAGES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --verify-local)
      VERIFY_LOCAL=1
      shift
      ;;
    --tag)
      TAG="${2:-}"
      [[ -n "$TAG" ]] || { echo "--tag requires a value" >&2; exit 1; }
      shift 2
      ;;
    --image)
      IMAGE_NAME="${2:-}"
      [[ -n "$IMAGE_NAME" ]] || { echo "--image requires a value" >&2; exit 1; }
      REQUESTED_IMAGES+=("$IMAGE_NAME")
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

declare -A DOCKERFILES=(
  [agent-base]="$REPO_ROOT/agents/charon/skills/bootstrap/images/agent-base/Dockerfile"
  [agent-charon]="$REPO_ROOT/agents/charon/skills/bootstrap/images/charon/Dockerfile"
  [agent-augur]="$REPO_ROOT/agents/charon/skills/bootstrap/images/augur/Dockerfile"
  [agent-alfred]="$REPO_ROOT/agents/charon/skills/bootstrap/images/alfred/Dockerfile"
  [agent-sauron]="$REPO_ROOT/agents/charon/skills/bootstrap/images/sauron/Dockerfile"
)

declare -a IMAGE_ORDER=(
  agent-base
  agent-charon
  agent-augur
  agent-alfred
  agent-sauron
)

if [[ ${#REQUESTED_IMAGES[@]} -eq 0 ]]; then
  REQUESTED_IMAGES=("${IMAGE_ORDER[@]}")
fi

build_and_push() {
  local name="$1"
  local dockerfile="${DOCKERFILES[$name]:-}"
  if [[ -z "$dockerfile" ]]; then
    echo "Unknown image: $name" >&2
    exit 1
  fi
  docker build \
    --build-arg REGISTRY="$REGISTRY" \
    -f "$dockerfile" \
    -t "$REGISTRY/$name:latest" \
    "$REPO_ROOT"
  if [[ -n "$TAG" ]]; then
    docker tag "$REGISTRY/$name:latest" "$REGISTRY/$name:$TAG"
  fi
  if [[ $VERIFY_LOCAL -eq 1 ]]; then
    "$REPO_ROOT/lib/scripts/verify-agent-image.sh" "$REGISTRY/$name:latest"
  fi
  docker push "$REGISTRY/$name:latest"
  if [[ -n "$TAG" ]]; then
    docker push "$REGISTRY/$name:$TAG"
  fi
}

for image in "${REQUESTED_IMAGES[@]}"; do
  build_and_push "$image"
done
