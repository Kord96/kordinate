#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <namespace> [kustomize_dir]" >&2
  exit 2
fi

namespace="$1"
kustomize_dir="${2:-/kord/workstation/home/project/kordinate/agents/charon/skills/platform/manifests/base}"

rendered="$(mktemp)"
trap 'rm -f "$rendered"' EXIT

kubectl kustomize "$kustomize_dir" >"$rendered"

if grep -q 'REGISTRY/' "$rendered"; then
  echo "refusing to apply unresolved platform manifests from: $kustomize_dir" >&2
  echo "rendered output still contains REGISTRY/ placeholders" >&2
  exit 1
fi

kubectl apply --server-side -f "$rendered" -n "$namespace"
