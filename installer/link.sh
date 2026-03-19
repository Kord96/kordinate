#!/bin/bash
# Link kordinate framework into paths that Claude Code and other tools expect.
#
# Usage:
#   ./installer/link.sh          # deploy: repo → ~/.claude/
#   ./installer/link.sh sync     # sync: ~/.claude/ → repo (renamed files only)
#
# Directories are symlinked (Claude reads/writes through them).
# Renamed files (AGENT.md → CLAUDE.md) are copied. Run "sync" to
# copy changes back before committing.
#
# See installer/LINKS.md for the full mapping.

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
# Symlinks: "link_name:target_path" — directories and files that
#   don't need renaming. Target paths relative to repo root.
#
# Copies: "dest_name:source_path" — files that need renaming
#   (AGENT.md → CLAUDE.md). Copied on deploy, synced back on sync.
# ═══════════════════════════════════════════════════════════════

# Claude Code conventions — symlinked
CLAUDE_SYMLINKS=(
  "settings.json:kordinate/settings.json"
  "keybindings.json:kordinate/profile/keybindings.json"
  ".mcp.json:kordinate/profile/mcp.json"
  "agents:kordinate/agents"
  "commands:kordinate/commands"
)

# Claude Code conventions — copied (renamed files)
# Format: "claude_path:kordinate_path"
# claude_path is relative to ~/.claude/
# kordinate_path is relative to repo root
CLAUDE_COPIES=(
  "CLAUDE.md:kordinate/agents/AGENT.md"
  "agents/deployer/CLAUDE.md:kordinate/agents/deployer/AGENT.md"
  "agents/sauron/CLAUDE.md:kordinate/agents/sauron/AGENT.md"
  "agents/designer/CLAUDE.md:kordinate/agents/designer/AGENT.md"
  "agents/scribe/CLAUDE.md:kordinate/agents/scribe/AGENT.md"
)

# Kordinate internal — symlinked
KORDINATE_SYMLINKS=(
  "hooks:kordinate/hooks"
  "profile:kordinate/profile"
  "agent-memory/deployer:kordinate/agents/deployer/memory/dynamic"
  "agent-memory/sauron:kordinate/agents/sauron/memory/dynamic"
  "agent-memory/designer:kordinate/agents/designer/memory/dynamic"
  "agent-memory/scribe:kordinate/agents/scribe/memory/dynamic"
)

# External resources — symlinked with absolute targets
EXTERNAL_LINKS=(
  "kordinate/profile/keystore:$HOME/.password-store/kordinate"
)

# ═══════════════════════════════════════════════════════════════
# PROJECT LINKING
#
# Links project-level agent dirs into .claude/agent-memory/.
# Agent dirs at project root follow the same static/dynamic
# split as global memory:
#
#   <project>/<agent>/static/    — pre-defined structure (manifests, dashboards)
#   <project>/<agent>/dynamic/   — free-form agent notes
#   .claude/agent-memory/<agent> → <agent>/dynamic/
#
# Only agents with existing project dirs get linked.
# ═══════════════════════════════════════════════════════════════

KNOWN_AGENTS=(deployer sauron designer scribe)

cmd_link_project() {
  local project_root
  project_root=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "Not in a git repo — skipping project linking"
    return 0
  }

  echo "=== Project agent linking ==="

  local linked=0
  for agent in "${KNOWN_AGENTS[@]}"; do
    local agent_dir="$project_root/$agent"
    [ -d "$agent_dir" ] || continue

    # Ensure static/ and dynamic/ exist
    mkdir -p "$agent_dir/static" "$agent_dir/dynamic"

    local target="$project_root/.claude/agent-memory/$agent"
    mkdir -p "$(dirname "$target")"

    if [ -L "$target" ]; then
      local current
      current=$(readlink "$target")
      if [ "$current" = "../../${agent}/dynamic" ]; then
        echo "  ok  $agent"
      else
        echo "  WARN $agent → $current (expected ../../${agent}/dynamic)" >&2
      fi
    elif [ -d "$target" ]; then
      # Existing real directory — migrate contents then link
      echo "  migrate $agent (moving contents to $agent/dynamic/)"
      cp -a "$target"/. "$agent_dir/dynamic/" 2>/dev/null || true
      rm -rf "$target"
      ln -s "../../${agent}/dynamic" "$target"
      echo "  +   $agent → $agent/dynamic/"
    else
      ln -s "../../${agent}/dynamic" "$target"
      echo "  +   $agent → $agent/dynamic/"
    fi
    linked=$((linked + 1))
  done

  if [ "$linked" -eq 0 ]; then
    echo "  (no agent dirs found at project root)"
  fi
  echo ""
  echo "Done."
}

# ═══════════════════════════════════════════════════════════════
# SYNC: copy modified CLAUDE.md files back to repo as AGENT.md
# ═══════════════════════════════════════════════════════════════

cmd_sync() {
  echo "=== Sync: ~/.claude/ → repo ==="
  for mapping in "${CLAUDE_COPIES[@]}"; do
    local claude_path="${mapping%%:*}"
    local repo_path="${mapping#*:}"
    local src="$TARGET/$claude_path"
    local dest="$REPO_ROOT/$repo_path"
    if [ -f "$src" ] && [ ! -L "$src" ]; then
      if ! diff -q "$src" "$dest" &>/dev/null; then
        cp "$src" "$dest"
        echo "  ←   $claude_path → $repo_path"
      else
        echo "  ok  $claude_path (unchanged)"
      fi
    fi
  done
  echo ""
  echo "Done."
}

# ═══════════════════════════════════════════════════════════════
# DEPLOY: repo → ~/.claude/
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

apply_symlinks() {
  local -n arr=$1
  for mapping in "${arr[@]}"; do
    local name="${mapping%%:*}"
    local source="${mapping#*:}"
    local dest="$TARGET/$name"
    local parent
    parent="$(dirname "$dest")"
    [ "$parent" != "$TARGET" ] && mkdir -p "$parent"
    create_link "$dest" "$REPO_ROOT/$source"
  done
}

deploy_copies() {
  for mapping in "${CLAUDE_COPIES[@]}"; do
    local claude_path="${mapping%%:*}"
    local repo_path="${mapping#*:}"
    local dest="$TARGET/$claude_path"
    local src="$REPO_ROOT/$repo_path"
    if [ -L "$dest" ]; then
      # Replace stale symlink with real file
      rm "$dest"
    fi
    if [ -f "$src" ]; then
      cp "$src" "$dest"
      echo "  +   $claude_path (copied from $repo_path)"
    fi
  done
}

cmd_deploy() {
  # Ensure ~/.claude exists as a real directory
  if [ ! -d "$TARGET" ] && [ ! -L "$TARGET" ]; then
    mkdir -p "$TARGET"
    echo "  Created $TARGET"
  elif [ -L "$TARGET" ]; then
    echo "  WARNING: ~/.claude is a symlink — removing to create directory"
    rm "$TARGET"
    mkdir -p "$TARGET"
  fi

  echo "=== Claude Code symlinks ==="
  apply_symlinks CLAUDE_SYMLINKS

  echo ""
  echo "=== Claude Code copies (renamed) ==="
  deploy_copies

  echo ""
  echo "=== Kordinate internal ==="
  apply_symlinks KORDINATE_SYMLINKS

  echo ""
  echo "=== External resource links ==="
  for mapping in "${EXTERNAL_LINKS[@]}"; do
    local link_path="${mapping%%:*}"
    local target="${mapping#*:}"
    local dest="$REPO_ROOT/$link_path"
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
}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

case "${1:-deploy}" in
  sync)         cmd_sync ;;
  deploy)       cmd_deploy ;;
  link-project) cmd_link_project ;;
  *)            echo "Usage: $0 [deploy|sync|link-project]"; exit 1 ;;
esac
