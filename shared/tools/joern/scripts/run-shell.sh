#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORKSPACE_DIR="${ROOT_DIR}/workspace"
IMAGE_TAG="${JOERN_IMAGE_TAG:-kordinate/joern:4.0.518}"

mkdir -p "${WORKSPACE_DIR}"

docker run --rm -it \
  -v "${WORKSPACE_DIR}:/workspace" \
  "${IMAGE_TAG}" \
  bash
