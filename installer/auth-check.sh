#!/bin/bash
# Auth check — runs on the workstation to verify and set up credentials.
# Called by setup.sh as the final step, or manually: bash /tmp/auth-check.sh
#
# Checks pass store for required keys. For missing ones, guides the user
# through the tool's normal auth flow and stores the result in pass.

set -euo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'
BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "  ${GREEN}ok${NC}    $*"; }
miss() { echo -e "  ${RED}miss${NC}  $*"; }
info() { echo -e "  ${YELLOW}→${NC}     $*"; }

NEEDS_HYDRATE=false

echo -e "${BOLD}Auth Check${NC}"
echo ""

# ─── GPG key ───
if gpg --list-secret-keys 2>/dev/null | grep -q '^sec'; then
  ok "GPG key"
else
  info "Generating GPG key..."
  gpg --batch --gen-key <<EOF
%no-protection
Key-Type: RSA
Key-Length: 4096
Name-Real: kordinate
Name-Email: kordinate@localhost
Expire-Date: 0
%commit
EOF
  ok "GPG key (generated)"
fi

GPG_KEY_ID=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep -m1 '^sec' | awk '{print $2}' | cut -d/ -f2)

# ─── Pass store ───
if [ -d "$HOME/.password-store" ]; then
  ok "Pass store"
else
  pass init "$GPG_KEY_ID"
  ok "Pass store (initialized)"
fi

# ─── GitHub ───
if pass show kordinate/github/token &>/dev/null 2>&1; then
  TOKEN=$(pass show kordinate/github/token)
  if [ "$TOKEN" != "PLACEHOLDER" ]; then
    ok "GitHub (pass:kordinate/github/token)"
    # Ensure gh is authed with this token
    if ! gh auth status &>/dev/null 2>&1; then
      echo "$TOKEN" | gh auth login --with-token 2>/dev/null
    fi
  else
    miss "GitHub token is PLACEHOLDER"
  fi
fi

if ! gh auth status &>/dev/null 2>&1; then
  miss "GitHub — starting auth flow..."
  gh auth login
  # Store the token in pass
  GH_TOKEN=$(gh auth token 2>/dev/null || true)
  if [ -n "$GH_TOKEN" ]; then
    echo "$GH_TOKEN" | pass insert -e kordinate/github/token 2>/dev/null
    ok "GitHub token saved to pass"
  fi
fi

# ─── Tailscale ───
check_pass_key() {
  local key="$1" label="$2"
  local val
  val=$(pass show "kordinate/$key" 2>/dev/null || true)
  if [ -n "$val" ] && [ "$val" != "PLACEHOLDER" ]; then
    ok "$label"
    return 0
  else
    miss "$label — not set in pass"
    return 1
  fi
}

if ! check_pass_key "tailscale/auth_key_workstation" "Tailscale auth key"; then
  info "Get an auth key from https://login.tailscale.com/admin/settings/keys"
  read -rp "  Tailscale auth key (tskey-auth-...): " TS_KEY
  if [ -n "$TS_KEY" ]; then
    echo "$TS_KEY" | pass insert -e kordinate/tailscale/auth_key_workstation 2>/dev/null
    ok "Tailscale auth key saved to pass"
  fi
fi

# Start tailscale if not running
TS_KEY=$(pass show kordinate/tailscale/auth_key_workstation 2>/dev/null || true)
if [ -n "$TS_KEY" ] && [ "$TS_KEY" != "PLACEHOLDER" ]; then
  if ! sudo tailscale status &>/dev/null 2>&1; then
    info "Starting Tailscale..."
    sudo tailscaled --state=/var/lib/tailscale/tailscaled.state &
    sleep 2
    sudo tailscale up --authkey="$TS_KEY" --hostname="${TS_HOSTNAME:-workstation}" --ssh
    ok "Tailscale up ($(sudo tailscale ip -4 2>/dev/null))"
  else
    ok "Tailscale (already running)"
  fi
fi

# ─── Claude ───
CLAUDE_CREDS="$HOME/.claude/.credentials.json"
if [ -f "$CLAUDE_CREDS" ]; then
  ok "Claude"
  # Sync to pass if not already stored
  if ! pass show kordinate/claude/credentials &>/dev/null 2>&1; then
    cat "$CLAUDE_CREDS" | pass insert -m kordinate/claude/credentials 2>/dev/null
    ok "Claude credentials saved to pass"
  fi
elif pass show kordinate/claude/credentials &>/dev/null 2>&1; then
  # Restore from pass
  mkdir -p "$(dirname "$CLAUDE_CREDS")"
  pass show kordinate/claude/credentials > "$CLAUDE_CREDS"
  ok "Claude (restored from pass)"
else
  miss "Claude — running login..."
  claude login 2>/dev/null || true
  if [ -f "$CLAUDE_CREDS" ]; then
    cat "$CLAUDE_CREDS" | pass insert -m kordinate/claude/credentials 2>/dev/null
    ok "Claude credentials saved to pass"
  else
    miss "Claude login failed — run 'claude login' manually"
  fi
fi

# ─── Optional keys (check but don't block) ───
echo ""
echo -e "${BOLD}Optional credentials:${NC}"
check_pass_key "grafana_admin/api_key" "Grafana API key" || true
check_pass_key "cloudflare/api_token" "Cloudflare API token" || true
check_pass_key "tailscale/api_key" "Tailscale API key" || true

# ─── Hydrate MCP config ───
echo ""
if command -v kord-hydrate &>/dev/null; then
  info "Hydrating MCP config..."
  kord-hydrate 2>/dev/null && ok "MCP config" || miss "MCP hydrate failed"
fi

echo ""
echo -e "${BOLD}Done.${NC} Run 'claude login' to complete setup."
