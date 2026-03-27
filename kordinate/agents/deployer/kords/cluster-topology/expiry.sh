#!/bin/bash
# Hash-based cache expiry. Exit 0 = fresh, exit 1 = stale.
KORD_DIR="$(cd "$(dirname "$0")" && pwd)"
KORDINATE_HOME="${KORDINATE_HOME:-$HOME/.kord}"
source "$KORDINATE_HOME/lib/cache.sh"

# Check if cached data exists
[ -f "$KORD_DIR/data.md" ] || exit 1

# Check input hash — stale if dependencies changed since last consultation
cache_check "$KORD_DIR/.hash" \
  "$KORDINATE_HOME/kordinate/agents/deployer/skills/infra/manifests/" \
  "$KORDINATE_HOME/kordinate/agents/deployer/skills/infra/topology.yaml" \
  "$KORDINATE_HOME/profile/config.yaml" \
  "$KORDINATE_HOME/profile/overlays/" \
  || exit 1

exit 0  # fresh
