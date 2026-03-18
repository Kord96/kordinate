#!/bin/bash
# Link kordinate framework into ~/.claude so Claude Code discovers it.
# Also creates external resource symlinks (pass keystore, mcp.json alias).
#
# Usage: ./installer/link.sh
#
# See installer/README.md for the full links manifest.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FRAMEWORK="$REPO_ROOT/kordinate"
TARGET="$HOME/.claude"

if [ ! -d "$FRAMEWORK" ]; then
  echo "ERROR: $FRAMEWORK not found" >&2
  exit 1
fi

echo "=== Claude Code discovery links ==="

# When ~/.claude is a real directory (current workstation setup),
# create individual symlinks inside it.
# When ~/.claude doesn't exist or is already a symlink, link the whole dir.
if [ -d "$TARGET" ] && [ ! -L "$TARGET" ]; then
  # ~/.claude is a real directory — create symlinks inside it
  for item in CLAUDE.md settings.json keybindings.json .mcp.json .gitattributes agents agent-memory commands hooks profile; do
    src="kordinate/$item"
    dest="$TARGET/$item"
    if [ -L "$dest" ]; then
      echo "  ok  $item"
    elif [ -e "$dest" ]; then
      echo "  SKIP $item (real file/dir exists — move it first)"
    else
      ln -s "$src" "$dest"
      echo "  +   $item → $src"
    fi
  done
elif [ -L "$TARGET" ]; then
  current=$(readlink -f "$TARGET")
  if [ "$current" = "$(readlink -f "$FRAMEWORK")" ]; then
    echo "  ok  ~/.claude → $FRAMEWORK"
  else
    echo "  ~/.claude points to $current, relinking"
    ln -sfn "$FRAMEWORK" "$TARGET"
    echo "  +   ~/.claude → $FRAMEWORK"
  fi
else
  ln -sfn "$FRAMEWORK" "$TARGET"
  echo "  +   ~/.claude → $FRAMEWORK"
fi

echo ""
echo "=== External resource links ==="

# profile/keystore → pass store
KEYSTORE="$FRAMEWORK/profile/keystore"
PASS_STORE="$HOME/.password-store/kordinate"
if [ -L "$KEYSTORE" ]; then
  echo "  ok  profile/keystore"
elif [ -d "$PASS_STORE" ]; then
  ln -s "$PASS_STORE" "$KEYSTORE"
  echo "  +   profile/keystore → $PASS_STORE"
else
  echo "  SKIP profile/keystore (pass store not found at $PASS_STORE)"
fi

# profile/mcp.json → ../.mcp.json
MCP_LINK="$FRAMEWORK/profile/mcp.json"
if [ -L "$MCP_LINK" ]; then
  echo "  ok  profile/mcp.json"
else
  ln -s ../.mcp.json "$MCP_LINK"
  echo "  +   profile/mcp.json → ../.mcp.json"
fi

echo ""
echo "=== PATH ==="

# Add bin/ to PATH if not already there
SHELL_RC="$HOME/.bashrc"
[ "$(uname)" = "Darwin" ] && SHELL_RC="$HOME/.zshrc"
MARKER="# kordinate"
if ! grep -q "$MARKER" "$SHELL_RC" 2>/dev/null; then
  cat >> "$SHELL_RC" <<EOF

$MARKER
export KORDINATE_HOME="$REPO_ROOT"
export PATH="$REPO_ROOT/bin:\$PATH"
EOF
  echo "  +   Added $REPO_ROOT/bin to PATH in $SHELL_RC"
else
  echo "  ok  PATH already configured"
fi

echo ""
echo "Done."
