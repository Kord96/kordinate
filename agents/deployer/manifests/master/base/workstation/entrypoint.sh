#!/bin/bash
# Workstation entrypoint — minimal boot. Auth is handled by auth-check.sh.
set -euo pipefail

# ─── Shell config (once) ───
if ! grep -q 'CLAUDE_HOME' ~/.bashrc 2>/dev/null; then
  cat >> ~/.bashrc <<'BASHRC'
export CLAUDE_HOME="$HOME/.claude"
export PATH="$CLAUDE_HOME/bin:$PATH"
alias claude="claude-session --dangerously-skip-permissions"
[ -f "$CLAUDE_HOME/bin/tmux-session.bash" ] && source "$CLAUDE_HOME/bin/tmux-session.bash"
BASHRC
fi

# .bash_profile so login shells (SSH) source .bashrc
if [ ! -f ~/.bash_profile ]; then
  cat > ~/.bash_profile <<'PROF'
[ -f ~/.bashrc ] && source ~/.bashrc
PROF
fi

export CLAUDE_HOME="$HOME/.claude"
export PATH="$CLAUDE_HOME/bin:$PATH"

# ─── SSH ───
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# ─── Tailscale (from pass if available, non-fatal) ───
TS_KEY=$(pass show kordinate/tailscale/auth_key_workstation 2>/dev/null || true)
if [ -n "$TS_KEY" ] && [ "$TS_KEY" != "PLACEHOLDER" ]; then
  echo "Starting tailscaled..."
  sudo tailscaled --state=/var/lib/tailscale/tailscaled.state --tun=userspace-networking &
  sleep 3
  # Logout stale sessions to avoid hostname collisions (workstation-1, -2, etc.)
  sudo tailscale logout 2>/dev/null || true
  sleep 1
  if sudo tailscale up --authkey="$TS_KEY" --hostname="${TS_HOSTNAME:-workstation}" --ssh 2>&1; then
    echo "Tailscale up: $(sudo tailscale ip -4)"
  else
    echo "WARNING: tailscale up failed — workstation will boot without SSH access"
  fi
else
  echo "Tailscale: no auth key in pass — run auth-check.sh to configure"
fi

# ─── Update kordinate (if repo exists) ───
if [ -d ~/.claude/.git ]; then
  git -C ~/.claude pull --ff-only 2>/dev/null || true
fi

echo "Workstation ready."
exec sleep infinity
