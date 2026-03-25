#!/bin/bash
# Beorn entrypoint — boot, sync, start MCP agent server.
# Same base image as workstation. Differs only in what runs at the end.
set -euo pipefail

# ─── Shell config (once) ───
if ! grep -q 'KORDINATE_HOME' ~/.bashrc 2>/dev/null; then
  cat >> ~/.bashrc <<'BASHRC'
export KORDINATE_HOME="$HOME/.kord"
export PATH="$KORDINATE_HOME/bin:$PATH"
BASHRC
fi

if [ ! -f ~/.bash_profile ]; then
  cat > ~/.bash_profile <<'PROF'
[ -f ~/.bashrc ] && source ~/.bashrc
PROF
fi

export KORDINATE_HOME="${KORDINATE_HOME:-$HOME/.kord}"
export PATH="$HOME/kordinate/bin:$PATH"

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
exec node "$MCP_SERVER/server.js"
