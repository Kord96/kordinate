#!/bin/bash
# Two-stage cache expiry. Exit 0 = fresh, 1 = stale, 2 = uncertain.
KORD_DIR="$(cd "$(dirname "$0")" && pwd)"
KORDINATE_HOME="${KORDINATE_HOME:-$HOME/.kord}"
source "$KORDINATE_HOME/lib/cache.sh"

# Stage 1: Deterministic checks
# No cached data → definitely stale
[ -s "$KORD_DIR/data.md" ] || exit 1

# Hash unchanged → definitely fresh
cache_check "$KORD_DIR/.hash" \
  "$KORDINATE_HOME/kordinate/agents/sauron/memory/" \
  "$KORDINATE_HOME/kordinate/agents/deployer/skills/infra/manifests/" \
  "$KORDINATE_HOME/kordinate/agents/deployer/skills/infra/dashboards/" \
  && exit 0

# Hash changed but cache exists → uncertain (needs agent review)
exit 2
