#!/bin/bash
# Workstation entrypoint — minimal boot. Auth is handled by auth-check.sh.
set -euo pipefail

# ─── Shell config (once) ───
if ! grep -q 'KORDINATE_HOME' ~/.bashrc 2>/dev/null; then
  cat >> ~/.bashrc <<'BASHRC'
export KORDINATE_HOME="$HOME/kordinate"
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

export KORDINATE_HOME="$HOME/kordinate"
export PATH="$KORDINATE_HOME/bin:$PATH"

# ─── SSH ───
mkdir -p ~/.ssh
chmod 700 ~/.ssh

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

# ─── Initialize kord shared state ───
if [ -n "${KORDINATE_HOME:-}" ] && [ -d "$KORDINATE_HOME" ]; then
  # Ensure worktree and lock directories exist
  mkdir -p "${KORD_WORKTREE_ROOT:-$KORDINATE_HOME/.worktrees}"
  mkdir -p "$KORDINATE_HOME/.locks"

  # Symlink ~/.kord -> KORDINATE_HOME for tools that expect it
  if [ ! -L "$HOME/.kord" ]; then
    rm -rf "$HOME/.kord" 2>/dev/null || true
    ln -sf "$KORDINATE_HOME" "$HOME/.kord"
    echo "Symlinked ~/.kord -> $KORDINATE_HOME"
  fi

  # Prune stale worktrees from previous crashes
  if [ -d "$KORDINATE_HOME/.git" ]; then
    git -C "$KORDINATE_HOME" worktree prune 2>/dev/null || true
  fi
fi

# ─── Update kordinate (if repo exists) ───
if [ -d ~/kordinate/.git ]; then
  git -C ~/kordinate pull --ff-only 2>/dev/null || true
fi

# ─── Start Beorn (MCP agent server) ───
MCP_SERVER="$HOME/kordinate/kordinate/lib/mcp-agent-server"
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
