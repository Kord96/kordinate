#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
IMAGE_TAG="${JOERN_IMAGE_TAG:-kordinate/joern:4.0.518}"

docker build -t "${IMAGE_TAG}" "${ROOT_DIR}"

echo "Built ${IMAGE_TAG}"
