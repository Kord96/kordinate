#!/bin/bash
# Remove koordinate-installed files from ~/.claude/ and shell profile.
# Does NOT remove ~/.claude/ itself, K8s secrets, or the repo.
#
# Usage: ./setup.sh uninstall

set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/lib.sh"

echo "Uninstalling koordinate..."

# ─── Remove commands ───
if [ -d "$CLAUDE_DIR/commands" ]; then
  for f in consult.md subagent-catchup.md; do
    if [ -f "$CLAUDE_DIR/commands/$f" ]; then
      rm "$CLAUDE_DIR/commands/$f"
      echo "  REMOVE commands/$f"
    fi
  done
  if [ -d "$CLAUDE_DIR/commands/scribe" ]; then
    rm -rf "$CLAUDE_DIR/commands/scribe"
    echo "  REMOVE commands/scribe/"
  fi
fi

# ─── Remove agents ───
if [ -d "$CLAUDE_DIR/agents" ]; then
  for agent in deployer sauron designer scribe; do
    if [ -d "$CLAUDE_DIR/agents/$agent" ]; then
      rm -rf "$CLAUDE_DIR/agents/$agent"
      echo "  REMOVE agents/$agent/"
    fi
  done
fi

# ─── Remove profile ───
if [ -d "$CLAUDE_DIR/profile" ]; then
  rm -rf "$CLAUDE_DIR/profile"
  echo "  REMOVE profile/"
fi

# ─── Remove framework and config files ───
for f in CLAUDE.md .mcp.json mcp-global.json config.yaml .scribe-secret .deployer-secret; do
  if [ -f "$CLAUDE_DIR/$f" ]; then
    rm "$CLAUDE_DIR/$f"
    echo "  REMOVE $f"
  fi
done

# ─── Remove agent-state ───
if [ -d "$CLAUDE_DIR/agent-state" ]; then
  rm -rf "$CLAUDE_DIR/agent-state"
  echo "  REMOVE agent-state/"
fi

# ─── Remove hooks ───
if [ -d "$CLAUDE_DIR/hooks" ]; then
  rm -rf "$CLAUDE_DIR/hooks"
  echo "  REMOVE hooks/"
fi

# ─── Remove settings.json ───
if [ -f "$CLAUDE_DIR/settings.json" ]; then
  rm "$CLAUDE_DIR/settings.json"
  echo "  REMOVE settings.json"
fi

# ─── Remove tmux config ───
if [ -f "$HOME/.tmux.conf" ]; then
  rm "$HOME/.tmux.conf"
  echo "  REMOVE ~/.tmux.conf"
fi

# ─── Clean shell RC ───
if [ -f "$SHELL_RC" ]; then
  TMPRC="$(mktemp)"
  grep -v -E '(koordinate|kordinate|CLAUDE_HOME|claude-session|tmux-session\.bash)' "$SHELL_RC" > "$TMPRC" 2>/dev/null || true
  sed -i '/^# koordinate/d; /^# Claude Code: auto-worktree/d; /^# Default working directory/d; /^# .* tools$/d; /^# koordinate home$/d; /^# koordinate tmux session/d' "$TMPRC"
  sed -i -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$TMPRC"
  mv "$TMPRC" "$SHELL_RC"
  echo "  CLEAN $SHELL_RC (removed koordinate entries)"
fi

echo ""
echo "Uninstall complete."
echo "  Kept: ~/.claude/ directory (empty), pass store (~/.password-store/kordinate/), repo"
echo "  To fully remove: rm -rf ~/.claude/ and delete the repo"
echo "  Pass store is not removed — manage it with: pass rm -r kordinate"
