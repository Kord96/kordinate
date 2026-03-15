#!/bin/bash
# Check prerequisites, framework installation, profile, and connectivity.
#
# Usage:
#   ./setup.sh doctor                   # full check
#   ./setup.sh doctor --quiet           # failures only
#   ./setup.sh doctor --category prereqs  # single category
#
# Exit: 0 = all pass, 1 = critical failure

set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"

QUIET=false
CATEGORY=""
FAILURES=0
WARNINGS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quiet|-q) QUIET=true; shift ;;
    --category|-c) CATEGORY="$2"; shift 2 ;;
    *) err "Unknown flag: $1"; exit 1 ;;
  esac
done

# Output helpers that respect --quiet
ok() {
  $QUIET || echo -e "  ${GREEN}PASS${NC}  $*"
}

fail() {
  echo -e "  ${RED}FAIL${NC}  $*"
  ((FAILURES++)) || true
}

skip() {
  $QUIET || echo -e "  ${YELLOW}SKIP${NC}  $*"
}

section() {
  $QUIET || echo -e "\n${BOLD}$*${NC}"
}

# ═══════════════════════════════════════════════
# PREREQS — required local tools
# ═══════════════════════════════════════════════
check_prereqs() {
  section "Prerequisites"

  local -A tools=(
    [git]="apt install git"
    [gh]="https://cli.github.com"
    [python3]="apt install python3"
    [openssl]="apt install openssl"
    [tmux]="apt install tmux"
    [claude]="npm i -g @anthropic-ai/claude-code"
    [curl]="apt install curl"
    [ssh]="apt install openssh-client"
    [gpg]="apt install gnupg"
    [pass]="apt install pass"
  )

  for tool in git gh python3 openssl tmux claude curl ssh gpg pass; do
    if command -v "$tool" &>/dev/null; then
      local ver
      case "$tool" in
        git)     ver=$(git --version 2>/dev/null | awk '{print $3}') ;;
        gh)      ver=$(gh --version 2>/dev/null | head -1 | awk '{print $3}') ;;
        python3) ver=$(python3 --version 2>/dev/null | awk '{print $2}') ;;
        openssl) ver=$(openssl version 2>/dev/null | awk '{print $2}') ;;
        tmux)    ver=$(tmux -V 2>/dev/null | awk '{print $2}') ;;
        claude)  ver=$(claude --version 2>/dev/null | head -1 || echo "?") ;;
        curl)    ver=$(curl --version 2>/dev/null | head -1 | awk '{print $2}') ;;
        ssh)     ver=$(ssh -V 2>&1 | awk '{print $1}') ;;
        gpg)     ver=$(gpg --version 2>/dev/null | head -1 | awk '{print $3}') ;;
        pass)    ver=$(command pass version 2>/dev/null | head -1 | grep -oP 'v[\d.]+' || echo "?") ;;
      esac
      ok "$tool ($ver)"
    else
      fail "$tool — install: ${tools[$tool]}"
    fi
  done
}

# ═══════════════════════════════════════════════
# FRAMEWORK — ~/.claude/ installation
# ═══════════════════════════════════════════════
check_framework() {
  section "Framework (~/.claude/)"

  # CLAUDE.md
  if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
    ok "CLAUDE.md"
  else
    fail "CLAUDE.md missing — run: ./setup.sh install"
  fi

  # Agents
  local agents_ok=true
  for agent in deployer sauron designer scribe; do
    if [ -d "$CLAUDE_DIR/agents/$agent" ] && [ -f "$CLAUDE_DIR/agents/$agent/CLAUDE.md" ]; then
      ok "agents/$agent/"
    else
      fail "agents/$agent/ missing — run: ./setup.sh install"
      agents_ok=false
    fi
  done

  # Commands
  if [ -d "$CLAUDE_DIR/commands" ] && [ "$(ls -A "$CLAUDE_DIR/commands" 2>/dev/null)" ]; then
    ok "commands/"
  else
    fail "commands/ empty — run: ./setup.sh install"
  fi

  # Scribe commands
  if [ -d "$CLAUDE_DIR/commands/scribe" ]; then
    ok "commands/scribe/"
  else
    fail "commands/scribe/ missing — run: ./setup.sh install"
  fi

  # Hooks
  if [ -d "$CLAUDE_DIR/hooks" ] && [ "$(ls "$CLAUDE_DIR/hooks"/*.sh 2>/dev/null)" ]; then
    local hook_count
    hook_count=$(ls "$CLAUDE_DIR/hooks"/*.sh 2>/dev/null | wc -l)
    ok "hooks/ ($hook_count scripts)"
  else
    fail "hooks/ missing — run: ./setup.sh install"
  fi

  # Settings
  if [ -f "$CLAUDE_DIR/settings.json" ] && grep -q 'guard-md.sh' "$CLAUDE_DIR/settings.json" 2>/dev/null; then
    ok "settings.json (hooks configured)"
  else
    fail "settings.json missing or hooks not configured — run: ./setup.sh install"
  fi

  # Auth secrets
  for agent_secret in scribe deployer sauron; do
    if [ -f "$CLAUDE_DIR/.${agent_secret}-secret" ]; then
      ok ".${agent_secret}-secret"
    else
      fail ".${agent_secret}-secret missing — run: ./setup.sh install"
    fi
  done
}

# ═══════════════════════════════════════════════
# PROFILE — sensitive config at ~/.claude/
# ═══════════════════════════════════════════════
check_profile() {
  section "Profile (~/.claude/)"

  # Pass store
  if [ -d "$HOME/.password-store/kordinate" ]; then
    ok "pass store (kordinate/)"
  else
    fail "pass store missing — run: ./setup.sh profile"
  fi

  # Required keys in pass
  local required_keys=(
    tailscale/api_key
    tailscale/auth_key_gateway
    grafana_admin/api_key
    gemini/api_key
    cloudflare/api_token
    cloudflare/tunnel_token
  )
  for key in "${required_keys[@]}"; do
    if pass show "kordinate/$key" &>/dev/null; then
      local val
      val=$(pass show "kordinate/$key" 2>/dev/null)
      if [ "$val" = "PLACEHOLDER" ]; then
        fail "pass:kordinate/$key is PLACEHOLDER"
      else
        ok "pass:kordinate/$key"
      fi
    else
      fail "pass:kordinate/$key missing — run: pass insert kordinate/$key"
    fi
  done

  # config.yaml
  if [ -f "$CLAUDE_DIR/profile/config.yaml" ]; then
    if grep -q '100\.x\.x\.x' "$CLAUDE_DIR/profile/config.yaml" 2>/dev/null; then
      fail "profile/config.yaml exists but contains placeholders (100.x.x.x)"
    else
      ok "profile/config.yaml (configured)"
    fi
  else
    fail "profile/config.yaml missing — run: ./setup.sh profile"
  fi

  # Root config.yaml
  if [ -f "$CLAUDE_DIR/config.yaml" ]; then
    ok "config.yaml"
  else
    fail "config.yaml missing — run: ./setup.sh profile"
  fi

  # .mcp.json (generated by hydrate)
  if [ -f "$CLAUDE_DIR/.mcp.json" ]; then
    ok ".mcp.json (generated)"
  else
    fail ".mcp.json missing — run: ./setup.sh hydrate"
  fi

  # Shell RC
  if [ -f "$SHELL_RC" ] && grep -q 'CLAUDE_HOME' "$SHELL_RC" 2>/dev/null; then
    ok "$SHELL_RC contains CLAUDE_HOME"
  else
    fail "$SHELL_RC missing CLAUDE_HOME — run: ./setup.sh shell"
  fi
}

# ═══════════════════════════════════════════════
# CONNECTIVITY — external services
# ═══════════════════════════════════════════════
check_connectivity() {
  section "Connectivity"

  # Skip if profile not configured
  if [ ! -f "$CLAUDE_DIR/profile/config.yaml" ] || grep -q '100\.x\.x\.x' "$CLAUDE_DIR/profile/config.yaml" 2>/dev/null; then
    skip "profile not configured — skipping connectivity checks"
    return
  fi

  # GitHub
  if gh auth status &>/dev/null; then
    ok "GitHub (gh auth)"
  else
    fail "GitHub — run: gh auth login"
  fi

  # Tailscale
  if command -v tailscale &>/dev/null && tailscale status &>/dev/null; then
    ok "Tailscale (connected)"
  else
    # Try pinging cluster IP instead
    local cluster_ip
    cluster_ip=$(python3 -c "import yaml; c=yaml.safe_load(open('$CLAUDE_DIR/config.yaml')); print(c['clusters']['home']['tailscale_ip'])" 2>/dev/null || true)
    if [ -n "$cluster_ip" ] && ssh -o ConnectTimeout=3 -o BatchMode=yes "$cluster_ip" true &>/dev/null; then
      ok "Cluster reachable via SSH ($cluster_ip)"
    else
      fail "Tailscale — not connected and cluster not reachable"
    fi
  fi

  # K8s access
  if setup_kc 2>/dev/null; then
    if _kc get nodes &>/dev/null 2>&1; then
      ok "K8s cluster (nodes reachable)"
    else
      fail "K8s — _kc configured but cannot reach nodes"
    fi
  else
    fail "K8s — no cluster access"
    return
  fi

  # K8s namespaces
  local ns_ok=true
  for ns in gateway master dev test prod; do
    if _kc get namespace "$ns" &>/dev/null 2>&1; then
      ok "namespace: $ns"
    else
      fail "namespace: $ns missing"
      ns_ok=false
    fi
  done

  # Workstation pod
  if _kc get pod -n master -l app=workstation --no-headers 2>/dev/null | grep -q Running; then
    ok "workstation pod (Running)"
  else
    skip "workstation pod not running"
  fi
}

# ═══════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════
$QUIET || echo -e "${BOLD}koordinate doctor${NC}"

if [ -n "$CATEGORY" ]; then
  case "$CATEGORY" in
    prereqs|prerequisites) check_prereqs ;;
    framework)             check_framework ;;
    profile)               check_profile ;;
    connectivity)          check_connectivity ;;
    *) err "Unknown category: $CATEGORY (prereqs|framework|profile|connectivity)"; exit 1 ;;
  esac
else
  check_prereqs
  check_framework
  check_profile
  check_connectivity
fi

# Summary
echo ""
if [ "$FAILURES" -gt 0 ]; then
  echo -e "${RED}${BOLD}$FAILURES failure(s)${NC}"
  exit 1
else
  $QUIET || echo -e "${GREEN}${BOLD}All checks passed${NC}"
  exit 0
fi
