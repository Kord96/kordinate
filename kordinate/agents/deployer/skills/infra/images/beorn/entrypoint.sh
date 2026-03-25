#!/bin/bash
# Beorn entrypoint — boot, sync, start MCP agent server.
# Same base image as workstation. Differs only in what runs at the end.
#
# Expects /kord-shared to be a PVC mount containing the kord git repo.
# Agents get isolated git worktrees; Beorn merges back to main after each run.
set -euo pipefail

# ─── KORDINATE_HOME on PVC ───
export KORDINATE_HOME="/kord-shared"
export KORD_WORKTREE_ROOT="/kord-shared/.worktrees"
export PATH="$HOME/kordinate/bin:$PATH"

# Validate PVC mount
if [ ! -d "$KORDINATE_HOME/.git" ]; then
  echo "[beorn] FATAL: $KORDINATE_HOME/.git not found — PVC not mounted or not initialized"
  exit 1
fi
echo "[beorn] PVC validated: $KORDINATE_HOME/.git exists"

# Create worktree and lock directories
mkdir -p "$KORD_WORKTREE_ROOT"
mkdir -p "$KORDINATE_HOME/.locks"

# Prune stale worktrees from previous crashes
echo "[beorn] Pruning stale worktrees..."
git -C "$KORDINATE_HOME" worktree prune 2>/dev/null || true

# Backward compatibility: symlink ~/.kord -> /kord-shared
if [ ! -L "$HOME/.kord" ]; then
  rm -rf "$HOME/.kord" 2>/dev/null || true
  ln -sf "$KORDINATE_HOME" "$HOME/.kord"
  echo "[beorn] Symlinked ~/.kord -> $KORDINATE_HOME"
fi

# ─── Shell config (once) ───
if ! grep -q 'KORDINATE_HOME' ~/.bashrc 2>/dev/null; then
  cat >> ~/.bashrc <<'BASHRC'
export KORDINATE_HOME="/kord-shared"
export KORD_WORKTREE_ROOT="/kord-shared/.worktrees"
export PATH="$KORDINATE_HOME/bin:$PATH"
BASHRC
fi

if [ ! -f ~/.bash_profile ]; then
  cat > ~/.bash_profile <<'PROF'
[ -f ~/.bashrc ] && source ~/.bashrc
PROF
fi

# ─── SSH ───
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# ─── Update repo (if exists) ───
if [ -d ~/kordinate/.git ]; then
  echo "[beorn] Pulling latest repo..."
  git -C ~/kordinate pull --ff-only 2>/dev/null || true
fi

# ─── Claude credentials (restore from pass on first boot) ───
CLAUDE_CREDS="$HOME/.claude/.credentials.json"
if [ ! -f "$CLAUDE_CREDS" ]; then
  if command -v pass &>/dev/null && pass show kordinate/claude/credentials &>/dev/null 2>&1; then
    mkdir -p "$(dirname "$CLAUDE_CREDS")"
    pass show kordinate/claude/credentials > "$CLAUDE_CREDS"
    echo "[beorn] Claude credentials restored from pass"
  else
    echo "[beorn] WARNING: no Claude credentials — run 'claude login' or seed pass"
  fi
else
  echo "[beorn] Claude credentials present"
fi

# ─── Install MCP server deps ───
MCP_SERVER="$KORDINATE_HOME/lib/mcp-agent-server"
if [ -d "$MCP_SERVER" ]; then
  echo "[beorn] Installing server dependencies..."
  cd "$MCP_SERVER"
  npm install --production 2>/dev/null || npm install 2>/dev/null || true
  cd -
fi

# ─── Start beorn ───
echo "[beorn] Starting shape-shifting agent server..."
echo "[beorn] KORDINATE_HOME=$KORDINATE_HOME"
echo "[beorn] KORD_WORKTREE_ROOT=$KORD_WORKTREE_ROOT"
exec node "$MCP_SERVER/server.js"
