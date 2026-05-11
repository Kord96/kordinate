#!/bin/bash
# Workstation entrypoint — minimal boot. Auth is handled by auth-check.sh.
set -euo pipefail

export KORD_ROOT="${KORD_ROOT:-/kord}"
export HOME="${HOME:-/home/claude}"
export WORKSTATION_HOME="${WORKSTATION_HOME:-$KORD_ROOT/workstation/home}"
export KORD_SOURCE_ROOT="${KORD_SOURCE_ROOT:-$HOME/repos/kordinate}"
export KORD_LOCAL_STATE="${KORD_LOCAL_STATE:-$HOME/.local/share/kordinate}"
export KORD_LOCKS_DIR="${KORD_LOCKS_DIR:-$KORD_LOCAL_STATE/locks}"
export KORD_WORKTREES_DIR="${KORD_WORKTREES_DIR:-$KORD_LOCAL_STATE/worktrees}"
export KORD_SESSION_STATE_DIR="${KORD_SESSION_STATE_DIR:-$HOME/.claude/session-state}"

PERSIST_ROOT="$(dirname "$WORKSTATION_HOME")"
LEGACY_ROOT="$KORD_ROOT/kordinate"
LEGACY_TMUX_LAYOUT="$KORD_ROOT/claude-home/tmux-layout.json"
LOCAL_BIN="$HOME/.local/bin"
CLAUDE_HOOKS_DIR="$HOME/.claude/hooks"
TMUX_STATE_DIR="$HOME/.local/state/kordinate"
KORD_PROFILE_STATE_DIR="$KORD_LOCAL_STATE/profile"
OWNERSHIP_STATE_FILE="$HOME/.claude/runtime-ownership.yaml"
CLAUDE_STATE_ENTRIES="projects history.jsonl sessions session-env tasks backups cache file-history shell-snapshots settings.json .mcp.json keybindings.json"
LEGACY_REPO_SNAPSHOT_ENTRIES=".git .gitignore CLAUDE.md README.md requirements.txt kordinate agents commands dashboards profile setup agent-memory config.yaml config.yaml.template shared"
LOCAL_HELPERS="legacy/claude-session legacy/session-status tmux-save tmux-restore tmux-session.bash tmux-new-window"
CLAUDE_HOOKS="guard.sh subagent-invocation-gate.sh"

ensure_persistent_home() {
  local uid gid current_target
  uid="$(id -u)"
  gid="$(id -g)"

  sudo mkdir -p "$WORKSTATION_HOME"
  sudo chown "$uid:$gid" "$PERSIST_ROOT" "$WORKSTATION_HOME" 2>/dev/null || true

  if [ -L "$HOME" ]; then
    current_target="$(readlink -f "$HOME" 2>/dev/null || true)"
    if [ "$current_target" != "$WORKSTATION_HOME" ]; then
      sudo rm -f "$HOME"
      sudo ln -sfn "$WORKSTATION_HOME" "$HOME"
    fi
    return
  fi

  if [ -d "$HOME" ] && [ -z "$(find "$WORKSTATION_HOME" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
    shopt -s dotglob nullglob
    if [ -n "$(printf '%s' "$HOME"/* 2>/dev/null)" ]; then
      sudo cp -a "$HOME"/. "$WORKSTATION_HOME/"
      sudo chown -R "$uid:$gid" "$WORKSTATION_HOME" 2>/dev/null || true
    fi
    shopt -u dotglob nullglob
  fi

  if [ -d "$HOME" ]; then
    sudo rm -rf "$HOME"
  fi

  sudo ln -sfn "$WORKSTATION_HOME" "$HOME"
}

copy_entries_if_missing() {
  local src_root="$1"
  local dst_root="$2"
  local entries="$3"
  local entry

  [ -d "$src_root" ] || return 0
  mkdir -p "$dst_root"
  for entry in $entries; do
    [ -e "$src_root/$entry" ] || continue
    [ -e "$dst_root/$entry" ] && continue
    cp -an "$src_root/$entry" "$dst_root/$entry"
  done
}

install_local_helpers() {
  local source_root="$1"
  local helper

  [ -d "$source_root" ] || return 0
  mkdir -p "$LOCAL_BIN"
  for helper in $LOCAL_HELPERS; do
    [ -f "$source_root/$helper" ] || continue
    cp -a "$source_root/$helper" "$LOCAL_BIN/$(basename "$helper")"
    chmod +x "$LOCAL_BIN/$(basename "$helper")" 2>/dev/null || true
  done
}

install_claude_hooks() {
  local source_root="$1"
  local hook

  [ -d "$source_root" ] || return 0
  mkdir -p "$CLAUDE_HOOKS_DIR"
  for hook in $CLAUDE_HOOKS; do
    [ -f "$source_root/$hook" ] || continue
    cp -a "$source_root/$hook" "$CLAUDE_HOOKS_DIR/$hook"
    chmod +x "$CLAUDE_HOOKS_DIR/$hook" 2>/dev/null || true
  done
}

sync_workstation_state() {
  mkdir -p "$HOME/.claude" "$CLAUDE_HOOKS_DIR" "$LOCAL_BIN" "$TMUX_STATE_DIR" "$KORD_LOCKS_DIR" "$KORD_WORKTREES_DIR" "$KORD_SESSION_STATE_DIR" "$KORD_PROFILE_STATE_DIR"

  if [ -d "$KORD_SOURCE_ROOT/bin" ]; then
    install_local_helpers "$KORD_SOURCE_ROOT/bin"
  else
    install_local_helpers "$LEGACY_ROOT/bin"
  fi

  if [ -d "$KORD_SOURCE_ROOT/hooks" ]; then
    install_claude_hooks "$KORD_SOURCE_ROOT/hooks"
  else
    install_claude_hooks "$LEGACY_ROOT/hooks"
  fi

  if [ -f "$KORD_SOURCE_ROOT/shared/runtime-ownership.yaml" ]; then
    cp -a "$KORD_SOURCE_ROOT/shared/runtime-ownership.yaml" "$OWNERSHIP_STATE_FILE"
  elif [ -f "$LEGACY_ROOT/shared/runtime-ownership.yaml" ] && [ ! -f "$OWNERSHIP_STATE_FILE" ]; then
    cp -a "$LEGACY_ROOT/shared/runtime-ownership.yaml" "$OWNERSHIP_STATE_FILE"
  fi

  if [ -f "$KORD_SOURCE_ROOT/shared/runtime/profile/config-acl.yaml" ]; then
    cp -a "$KORD_SOURCE_ROOT/shared/runtime/profile/config-acl.yaml" "$KORD_PROFILE_STATE_DIR/config-acl.yaml"
  elif [ -f "$LEGACY_ROOT/shared/runtime/profile/config-acl.yaml" ] && [ ! -f "$KORD_PROFILE_STATE_DIR/config-acl.yaml" ]; then
    cp -a "$LEGACY_ROOT/shared/runtime/profile/config-acl.yaml" "$KORD_PROFILE_STATE_DIR/config-acl.yaml"
  fi

  if [ -d "$KORD_SOURCE_ROOT/shared/runtime/profile/locks" ] && [ -z "$(find "$KORD_LOCKS_DIR" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
    cp -an "$KORD_SOURCE_ROOT/shared/runtime/profile/locks/." "$KORD_LOCKS_DIR/"
  elif [ -d "$LEGACY_ROOT/shared/runtime/profile/locks" ] && [ -z "$(find "$KORD_LOCKS_DIR" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
    cp -an "$LEGACY_ROOT/shared/runtime/profile/locks/." "$KORD_LOCKS_DIR/"
  fi

  if [ -f "$LEGACY_TMUX_LAYOUT" ] && [ ! -f "$TMUX_STATE_DIR/tmux-layout.json" ]; then
    cp -an "$LEGACY_TMUX_LAYOUT" "$TMUX_STATE_DIR/tmux-layout.json"
  fi

  mkdir -p "$HOME/.claude/bin"
  [ -e "$LOCAL_BIN/claude-session" ] && ln -sfn "$LOCAL_BIN/claude-session" "$HOME/.claude/bin/claude-session"
  [ -e "$LOCAL_BIN/tmux-new-window" ] && ln -sfn "$LOCAL_BIN/tmux-new-window" "$HOME/.claude/bin/tmux-new-window"
}

migrate_legacy_state() {
  if [ -d "$LEGACY_ROOT" ]; then
    if [ -L "$HOME/.claude" ] && [ "$(readlink -f "$HOME/.claude" 2>/dev/null || true)" = "$LEGACY_ROOT" ]; then
      rm -f "$HOME/.claude"
    fi

    copy_entries_if_missing "$LEGACY_ROOT" "$HOME/.claude" "$CLAUDE_STATE_ENTRIES"
    copy_entries_if_missing "$LEGACY_ROOT" "$KORD_LOCAL_STATE/legacy-repo" "$LEGACY_REPO_SNAPSHOT_ENTRIES"
  fi
}

ensure_shell_config() {
  if ! grep -q 'KORD_LOCAL_STATE' ~/.bashrc 2>/dev/null; then
    cat >> ~/.bashrc <<'BASHRC'
export KORD_ROOT="${KORD_ROOT:-/kord}"
export WORKSTATION_HOME="${WORKSTATION_HOME:-$HOME}"
export KORD_SOURCE_ROOT="${KORD_SOURCE_ROOT:-$HOME/repos/kordinate}"
export KORD_LOCAL_STATE="${KORD_LOCAL_STATE:-$HOME/.local/share/kordinate}"
export KORD_LOCKS_DIR="${KORD_LOCKS_DIR:-$KORD_LOCAL_STATE/locks}"
export KORD_WORKTREES_DIR="${KORD_WORKTREES_DIR:-$KORD_LOCAL_STATE/worktrees}"
export KORD_SESSION_STATE_DIR="${KORD_SESSION_STATE_DIR:-$HOME/.claude/session-state}"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
alias openclaude="NODE_OPTIONS=\"--max-old-space-size=4096\" claude-session --dangerously-skip-permissions"
[ -f "$HOME/.local/bin/tmux-session.bash" ] && source "$HOME/.local/bin/tmux-session.bash"
BASHRC
  fi

  python3 - <<'PY'
from pathlib import Path
bashrc = Path.home() / '.bashrc'
text = bashrc.read_text()
replacements = {
    'export KORDINATE_HOME="$HOME/kordinate"\n': '',
    'export PATH="$HOME/.npm-global/bin:$KORDINATE_HOME/bin:$PATH"\n': 'export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"\n',
    '[ -f "$KORDINATE_HOME/bin/tmux-session.bash" ] && source "$KORDINATE_HOME/bin/tmux-session.bash"\n': '[ -f "$HOME/.local/bin/tmux-session.bash" ] && source "$HOME/.local/bin/tmux-session.bash"\n',
    'export PATH="$HOME/.npm-global/bin:$WORKSTATION_HOME/kordinate/bin:$PATH"\n': 'export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"\n',
    '[ -f "$WORKSTATION_HOME/kordinate/bin/tmux-session.bash" ] && source "$WORKSTATION_HOME/kordinate/bin/tmux-session.bash"\n': '[ -f "$HOME/.local/bin/tmux-session.bash" ] && source "$HOME/.local/bin/tmux-session.bash"\n',
}
for old, new in replacements.items():
    text = text.replace(old, new)
bashrc.write_text(text)
PY

  if [ ! -f ~/.bash_profile ]; then
    cat > ~/.bash_profile <<'PROF'
[ -f ~/.bashrc ] && source ~/.bashrc
PROF
  fi
}

ensure_persistent_home
migrate_legacy_state
sync_workstation_state
ensure_shell_config

mkdir -p "$HOME/.claude" "$HOME/projects" "$KORD_LOCAL_STATE/state"

ln -sfn "$KORD_ROOT/alfred/pass" "$HOME/.password-store"
ln -sfn "$KORD_ROOT/alfred/ssh" "$HOME/.ssh"
ln -sfn "$KORD_ROOT/alfred/gnupg" "$HOME/.gnupg"
ln -sfn "$KORD_ROOT/shared/repos" "$HOME/repos"
chmod 700 "$KORD_ROOT/alfred/pass" "$KORD_ROOT/alfred/ssh" "$KORD_ROOT/alfred/gnupg" 2>/dev/null || true

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

# Start sshd on port 2222 for Cloudflare tunnel SSH access.
# Port 22 is reserved for Tailscale SSH (identity-based, internal tailnet).
# Cloudflare tunnel routes ssh.khaledkord.com → localhost:2222 → sshd.
sudo ssh-keygen -A 2>/dev/null
sudo /usr/sbin/sshd -p 2222 2>/dev/null && echo "sshd started on port 2222 (Cloudflare)" || echo "WARNING: sshd failed to start"

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
  sudo tailscaled --state=/var/lib/tailscale/tailscaled.state &
  sleep 3
  if sudo tailscale up --authkey="$TS_KEY" --hostname="${TS_HOSTNAME:-workstation}" --ssh 2>&1; then
    echo "Tailscale up: $(sudo tailscale ip -4)"
  else
    echo "WARNING: tailscale up failed — workstation will boot without SSH access"
  fi
else
  echo "Tailscale: no auth key in pass — run auth-check.sh to configure"
fi

# ─── Git config for NFS ───
# NFS causes git index-pack to create read-only temp files that fail on read-back.
# Unpack to loose objects instead of pack files to avoid this.
git config --global transfer.unpackLimit 10000

# ─── Hydrate MCP config ───
kord-hydrate 2>/dev/null || echo "WARNING: kord-hydrate failed — MCP config not generated"

# ─── Restore tmux layout from standard user path ───
if [ -x "$LOCAL_BIN/tmux-restore" ]; then
  "$LOCAL_BIN/tmux-restore" || echo "WARNING: tmux-restore failed — starting with empty tmux"
fi

# ─── Periodic tmux layout save (every 60s) ───
if [ -x "$LOCAL_BIN/tmux-save" ]; then
  (while true; do sleep 60; "$LOCAL_BIN/tmux-save" 2>/dev/null; done) &
  echo "tmux auto-save started (every 60s)"
fi

echo "Workstation ready."
exec sleep infinity
