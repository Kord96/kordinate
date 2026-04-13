#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 /abs/path/to/cpg.bin /abs/path/to/query.sc [extra joern args...]" >&2
  exit 1
fi

CPG_PATH="$1"
QUERY_PATH="$2"
shift 2

if [[ ! -f "${CPG_PATH}" ]]; then
  echo "cpg does not exist: ${CPG_PATH}" >&2
  exit 1
fi

if [[ ! -f "${QUERY_PATH}" ]]; then
  echo "query script does not exist: ${QUERY_PATH}" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORKSPACE_DIR="${ROOT_DIR}/workspace"
IMAGE_TAG="${JOERN_IMAGE_TAG:-kordinate/joern:4.0.518}"

mkdir -p "${WORKSPACE_DIR}/scripts"
SCRIPT_BASENAME="$(basename "${QUERY_PATH}")"
cp "${QUERY_PATH}" "${WORKSPACE_DIR}/scripts/${SCRIPT_BASENAME}"

docker run --rm \
  -v "$(dirname "${CPG_PATH}"):/cpgdir:ro" \
  -v "${WORKSPACE_DIR}:/workspace" \
  "${IMAGE_TAG}" \
  bash -lc "joern --script /workspace/scripts/${SCRIPT_BASENAME} --params cpgFile=/cpgdir/$(basename "${CPG_PATH}") $*"
