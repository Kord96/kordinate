#!/bin/bash
# Workstation entrypoint — minimal boot. Auth is handled by auth-check.sh.
set -euo pipefail

# ─── Shell config (once) ───
if ! grep -q 'KORDINATE_HOME' ~/.bashrc 2>/dev/null; then
  cat >> ~/.bashrc <<'BASHRC'
export KORD_ROOT="${KORD_ROOT:-/kord}"
export KORDINATE_HOME="${KORDINATE_HOME:-$KORD_ROOT/kordinate}"
export PATH="$KORDINATE_HOME/bin:$PATH"
alias claude="claude-session --dangerously-skip-permissions"
[ -f "$KORDINATE_HOME/bin/tmux-session.bash" ] && source "$KORDINATE_HOME/bin/tmux-session.bash"
BASHRC
fi

# .bash_profile so login shells (SSH) source .bashrc
if [ ! -f ~/.bash_profile ]; then
  cat > ~/.bash_profile <<'PROF'
[ -f ~/.bashrc ] && source ~/.bashrc
PROF
fi

export KORD_ROOT="${KORD_ROOT:-/kord}"
export KORDINATE_HOME="${KORDINATE_HOME:-$KORD_ROOT/kordinate}"
export PATH="$KORDINATE_HOME/bin:$PATH"

# ─── Symlink persistent state from /kord into ephemeral home ───
ln -sfn "$KORD_ROOT/pass" "$HOME/.password-store"
ln -sfn "$KORD_ROOT/ssh" "$HOME/.ssh"
ln -sfn "$KORDINATE_HOME" "$HOME/.kord"
ln -sfn "$KORD_ROOT/projects" "$HOME/projects"
chmod 700 "$KORD_ROOT/pass" "$KORD_ROOT/ssh" 2>/dev/null || true

# Provision authorized keys from pass store (key-based auth fallback)
SSH_KEY=$(pass show kordinate/ssh/authorized_key 2>/dev/null || true)
if [ -n "$SSH_KEY" ]; then
  echo "$SSH_KEY" > ~/.ssh/authorized_keys
  chmod 600 ~/.ssh/authorized_keys
  echo "SSH authorized key provisioned from pass"
fi

# Set password for SSH access via Cloudflare tunnel.
# Cloudflare Access SSO gates the connection; password is a second factor.
SSH_PASS=$(pass show kordinate/ssh/password 2>/dev/null || true)
if [ -n "$SSH_PASS" ]; then
  echo "claude:$SSH_PASS" | sudo chpasswd
  # Expire password so first interactive login forces a change.
  # Once changed, the user's new password persists on the kord PVC.
  # After key exchange via 'kordinate connect', password is rarely used.
  sudo passwd --expire claude 2>/dev/null
  echo "SSH password set from pass (expired — will force change on first login)"
else
  echo "WARNING: no SSH password in pass (kordinate/ssh/password)"
fi

# Start sshd as a fallback so the workstation is reachable even if Tailscale SSH fails.
# Generate host keys if missing (first boot), then start sshd on port 22.
sudo ssh-keygen -A 2>/dev/null
sudo /usr/sbin/sshd 2>/dev/null && echo "sshd started on port 22" || echo "WARNING: sshd failed to start"

# ─── Tailscale (from pass if available, non-fatal) ───
TS_KEY=$(pass show kordinate/tailscale/auth_key_workstation 2>/dev/null || true)
if [ -n "$TS_KEY" ] && [ "$TS_KEY" != "PLACEHOLDER" ]; then
  # Delete stale workstation nodes via API and wait for propagation
  TS_API=$(pass show kordinate/tailscale/api_key 2>/dev/null || true)
  if [ -n "$TS_API" ]; then
    curl -sf -H "Authorization: Bearer $TS_API" "https://api.tailscale.com/api/v2/tailnet/-/devices" 2>/dev/null \
      | python3 -c "
import json,sys
for d in json.load(sys.stdin).get('devices',[]):
    if 'workstation' in d.get('hostname','').lower():
        print(d['id'])
" 2>/dev/null | while read id; do
      curl -sf -X DELETE -H "Authorization: Bearer $TS_API" "https://api.tailscale.com/api/v2/device/$id" 2>/dev/null
    done

    # Wait until control plane confirms no workstation devices remain
    for i in $(seq 1 12); do
      COUNT=$(curl -sf -H "Authorization: Bearer $TS_API" "https://api.tailscale.com/api/v2/tailnet/-/devices" 2>/dev/null \
        | python3 -c "
import json,sys
print(sum(1 for d in json.load(sys.stdin).get('devices',[]) if 'workstation' in d.get('hostname','').lower()))
" 2>/dev/null || echo "0")
      [ "$COUNT" = "0" ] && break
      sleep 5
    done
    echo "Cleaned stale workstation nodes"
  fi

  echo "Starting tailscaled..."
  sudo tailscaled --state=/var/lib/tailscale/tailscaled.state --tun=userspace-networking &
  sleep 3
  if sudo tailscale up --authkey="$TS_KEY" --hostname="${TS_HOSTNAME:-workstation}" --ssh 2>&1; then
    echo "Tailscale up: $(sudo tailscale ip -4)"
  else
    echo "WARNING: tailscale up failed — workstation will boot without SSH access"
  fi
else
  echo "Tailscale: no auth key in pass — run auth-check.sh to configure"
fi

# ─── Initialize kord state ───
mkdir -p "${KORD_WORKTREE_ROOT:-$KORDINATE_HOME/.worktrees}"
mkdir -p "$KORDINATE_HOME/.locks"
if [ -d "$KORDINATE_HOME/.git" ]; then
  git -C "$KORDINATE_HOME" worktree prune 2>/dev/null || true
fi

# ─── Update kordinate (if runtime repo exists) ───
if [ -d "$KORDINATE_HOME/.git" ]; then
  git -C "$KORDINATE_HOME" pull --ff-only 2>/dev/null || true
fi

# ─── Hydrate MCP config ───
kord-hydrate 2>/dev/null || echo "WARNING: kord-hydrate failed — MCP config not generated"

# ─── Start Beorn (MCP agent server) ───
MCP_SERVER="$KORDINATE_HOME/lib/mcp-agent-server"
if [ -d "$MCP_SERVER" ]; then
  echo "Installing Beorn dependencies..."
  (cd "$MCP_SERVER" && npm install --production 2>/dev/null || npm install 2>/dev/null || true)
  echo "Starting Beorn MCP agent server on port ${PORT:-3100}..."
  export PORT="${PORT:-3100}"
  node "$MCP_SERVER/server.js" &
  BEORN_PID=$!
  sleep 2
  if kill -0 "$BEORN_PID" 2>/dev/null; then
    echo "Beorn started (PID $BEORN_PID)"
  else
    echo "WARNING: Beorn failed to start — workstation continues without MCP agent server"
  fi
else
  echo "WARNING: MCP agent server not found at $MCP_SERVER — Beorn not started"
fi

echo "Workstation ready."
exec sleep infinity
