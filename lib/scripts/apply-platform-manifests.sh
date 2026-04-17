#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <namespace> [kustomize_dir]" >&2
  exit 2
fi

namespace="$1"
kustomize_dir="${2:-/kord/workstation/home/project/kordinate/agents/charon/skills/platform/manifests/base}"

kubectl apply --server-side -k "$kustomize_dir" -n "$namespace"
