#!/bin/bash
# Link kordinate framework into ~/.claude so Claude Code discovers it.
#
# Usage: ./link.sh
#   Creates:  ~/.claude → <repo>/kordinate/
#   Adds:     <repo>/bin/ to PATH via shell RC

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMEWORK="$SCRIPT_DIR/kordinate"
TARGET="$HOME/.claude"

if [ ! -d "$FRAMEWORK" ]; then
  echo "ERROR: $FRAMEWORK not found" >&2
  exit 1
fi

# Link ~/.claude → kordinate/
if [ -L "$TARGET" ]; then
  current=$(readlink -f "$TARGET")
  if [ "$current" = "$(readlink -f "$FRAMEWORK")" ]; then
    echo "~/.claude already linked to $FRAMEWORK"
  else
    echo "~/.claude points to $current, relinking to $FRAMEWORK"
    ln -sfn "$FRAMEWORK" "$TARGET"
  fi
elif [ -d "$TARGET" ]; then
  echo "ERROR: ~/.claude is a real directory. Back it up first:" >&2
  echo "  mv ~/.claude ~/.claude.bak" >&2
  exit 1
else
  ln -sfn "$FRAMEWORK" "$TARGET"
  echo "Linked ~/.claude → $FRAMEWORK"
fi

# Add bin/ to PATH if not already there
SHELL_RC="$HOME/.bashrc"
[ "$(uname)" = "Darwin" ] && SHELL_RC="$HOME/.zshrc"
MARKER="# kordinate"
if ! grep -q "$MARKER" "$SHELL_RC" 2>/dev/null; then
  cat >> "$SHELL_RC" <<EOF

$MARKER
export PATH="$SCRIPT_DIR/bin:\$PATH"
EOF
  echo "Added $SCRIPT_DIR/bin to PATH in $SHELL_RC"
else
  echo "PATH already configured in $SHELL_RC"
fi

echo "Done."
