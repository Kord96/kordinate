#!/bin/bash
# Shared setup utilities. Source this, don't execute it.

CLAUDE_HOME="${CLAUDE_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
CLAUDE_DIR="$HOME/.claude"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${GREEN}  ✓${NC} $*"; }
warn() { echo -e "${YELLOW}  !${NC} $*"; }
err()  { echo -e "${RED}  ✗${NC} $*"; }
info() { echo -e "${BLUE}  i${NC} $*"; }

# Shell RC: Darwin → .zshrc, else .bashrc
if [[ "$(uname)" == "Darwin" ]]; then
  SHELL_RC="$HOME/.zshrc"
else
  SHELL_RC="$HOME/.bashrc"
fi

# Kubectl resolver: in-cluster direct, external via SSH.
# After calling setup_kc, use _kc in place of kubectl.
# Returns 1 if no cluster access is available.
setup_kc() {
  if kubectl get nodes &>/dev/null 2>&1; then
    _kc() { kubectl "$@"; }
  else
    local config="$CLAUDE_DIR/config.yaml"
    local default_node
    default_node=$(python3 -c "import yaml; c=yaml.safe_load(open('$config')); print(c['clusters']['home']['tailscale_ip'])" 2>/dev/null || true)
    local node="${GIT_CRYPT_NODE:-${default_node:-}}"
    if [ -z "$node" ]; then
      _kc() { return 1; }
      return 1
    fi
    local kc="sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml"
    _kc() {
      if [ ! -t 0 ]; then
        ssh "$node" "$kc $*" < /dev/stdin
      else
        ssh "$node" "$kc $*"
      fi
    }
  fi
}
