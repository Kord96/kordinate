#!/bin/bash
# Link kordinate framework into paths that Claude Code and other tools expect.
#
# Usage: ./installer/link.sh
#
# The mapping below decouples Claude Code conventions from kordinate's
# internal structure. If kordinate reorganizes, update the mapping —
# Claude Code and hooks continue to work unchanged.
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

# ═══════════════════════════════════════════════════════════════
# MAPPING
#
# Format: "link_name:target_path"
# Link names are relative to ~/.claude/
# Target paths are relative to the repo root (made absolute at link time)
# ═══════════════════════════════════════════════════════════════

# Claude Code conventions — Claude discovers these at ~/.claude/
CLAUDE_LINKS=(
  "CLAUDE.md:kordinate/CLAUDE.md"
  "settings.json:kordinate/profile/settings.json"
  "keybindings.json:kordinate/profile/keybindings.json"
  ".mcp.json:kordinate/profile/mcp.json"
  "agents:kordinate/agents"
  "commands:kordinate/commands"
)

# Kordinate internal — NOT Claude conventions, linked so hooks/scripts
# can reference them at stable ~/.claude/ paths
KORDINATE_LINKS=(
  "hooks:kordinate/hooks"
  "profile:kordinate/profile"
  "agent-memory:kordinate/agents/memory"
  ".gitattributes:kordinate/.gitattributes"
)

# External resources — absolute targets outside the repo
EXTERNAL_LINKS=(
  "kordinate/profile/keystore:$HOME/.password-store/kordinate"
)

# ═══════════════════════════════════════════════════════════════
# APPLY LINKS
# ═══════════════════════════════════════════════════════════════

create_link() {
  local dest="$1" src="$2"
  if [ -L "$dest" ]; then
    echo "  ok  $(basename "$dest")"
  elif [ -e "$dest" ]; then
    echo "  SKIP $(basename "$dest") (real file/dir exists)"
  else
    ln -s "$src" "$dest"
    echo "  +   $(basename "$dest") → $src"
  fi
}

# Ensure ~/.claude exists as a real directory
if [ ! -d "$TARGET" ] && [ ! -L "$TARGET" ]; then
  mkdir -p "$TARGET"
  echo "  Created $TARGET"
elif [ -L "$TARGET" ]; then
  echo "  WARNING: ~/.claude is a symlink — removing to create directory"
  rm "$TARGET"
  mkdir -p "$TARGET"
fi

apply_links() {
  local -n arr=$1
  for mapping in "${arr[@]}"; do
    local name="${mapping%%:*}"
    local source="${mapping#*:}"
    create_link "$TARGET/$name" "$REPO_ROOT/$source"
  done
}

echo "=== Claude Code conventions ==="
apply_links CLAUDE_LINKS

echo ""
echo "=== Kordinate internal ==="
apply_links KORDINATE_LINKS

echo ""
echo "=== External resource links ==="

for mapping in "${EXTERNAL_LINKS[@]}"; do
  link_path="${mapping%%:*}"
  target="${mapping#*:}"
  dest="$REPO_ROOT/$link_path"

  if [ -L "$dest" ]; then
    echo "  ok  $link_path"
  elif [[ "$target" == /* ]] && [ ! -e "$target" ]; then
    echo "  SKIP $link_path (target not found: $target)"
  else
    ln -s "$target" "$dest"
    echo "  +   $link_path → $target"
  fi
done

echo ""
echo "=== PATH ==="

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
