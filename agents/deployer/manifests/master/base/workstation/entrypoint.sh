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
  # Delete stale workstation nodes via API to avoid hostname collisions
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

# ─── Update kordinate (if repo exists) ───
if [ -d ~/.claude/.git ]; then
  git -C ~/.claude pull --ff-only 2>/dev/null || true
fi

echo "Workstation ready."
exec sleep infinity
