#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 3 ]]; then
  echo "usage: $0 /abs/path/to/repo [language] [repo-id]" >&2
  exit 1
fi

REPO_PATH="$1"
LANGUAGE="${2:-}"
REPO_ID="${3:-$(basename "${REPO_PATH}")}"

if [[ ! -d "${REPO_PATH}" ]]; then
  echo "repo path does not exist: ${REPO_PATH}" >&2
  exit 1
fi

if [[ "${REPO_PATH}" != /* ]]; then
  echo "repo path must be absolute: ${REPO_PATH}" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORKSPACE_DIR="${ROOT_DIR}/workspace"
IMAGE_TAG="${JOERN_IMAGE_TAG:-kordinate/joern:4.0.518}"

if [[ -z "${LANGUAGE}" ]]; then
  LANGUAGE="$(python3 "${ROOT_DIR}/../repo_profile/detect_repo_profile.py" "${REPO_PATH}" --field dominant_language)"
fi

mkdir -p "${WORKSPACE_DIR}/cpgs"

case "${LANGUAGE}" in
  java) FRONTEND="/opt/joern/joern-cli/javasrc2cpg" ;;
  c) FRONTEND="/opt/joern/joern-cli/c2cpg.sh" ;;
  cpp) FRONTEND="/opt/joern/joern-cli/c2cpg.sh" ;;
  javascript) FRONTEND="/opt/joern/joern-cli/jssrc2cpg.sh" ;;
  python) FRONTEND="/opt/joern/joern-cli/pysrc2cpg" ;;
  go) FRONTEND="/opt/joern/joern-cli/gosrc2cpg" ;;
  kotlin) FRONTEND="/opt/joern/joern-cli/kotlin2cpg" ;;
  csharp) FRONTEND="/opt/joern/joern-cli/csharpsrc2cpg" ;;
  ghidra) FRONTEND="/opt/joern/joern-cli/ghidra2cpg" ;;
  jimple) FRONTEND="/opt/joern/joern-cli/jimple2cpg" ;;
  php) FRONTEND="/opt/joern/joern-cli/php2cpg" ;;
  ruby) FRONTEND="/opt/joern/joern-cli/rubysrc2cpg" ;;
  swift) FRONTEND="/opt/joern/joern-cli/swiftsrc2cpg.sh" ;;
  *)
    echo "unsupported language: ${LANGUAGE}" >&2
    exit 1
    ;;
esac

SAFE_ID="$(printf '%s' "${REPO_ID}-${LANGUAGE}" | tr '/: ' '---')"
OUTPUT_DIR="${WORKSPACE_DIR}/cpgs/${SAFE_ID}"
OUTPUT_PATH="${OUTPUT_DIR}/cpg.bin"

mkdir -p "${OUTPUT_DIR}"

docker run --rm \
  -v "${REPO_PATH}:/repo:ro" \
  -v "${WORKSPACE_DIR}:/workspace" \
  "${IMAGE_TAG}" \
  "${FRONTEND}" /repo -o "/workspace/cpgs/${SAFE_ID}/cpg.bin"

echo "${OUTPUT_PATH}"
