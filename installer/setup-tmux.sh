#!/bin/bash
# Set up tmux configuration: .tmux.conf, shell integration, and helper scripts.
#
# Usage: ./installer/setup-tmux.sh
#
# Idempotent — safe to run repeatedly.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BIN_DIR="$REPO_ROOT/bin"

SHELL_RC="$HOME/.bashrc"
[ "$(uname)" = "Darwin" ] && SHELL_RC="$HOME/.zshrc"

echo "=== tmux setup ==="

# ── .tmux.conf ──────────────────────────────────────────────

TMUX_CONF="$HOME/.tmux.conf"
cat > "$TMUX_CONF" << 'EOF'
set -g default-terminal "screen-256color"
set -g mouse on
set -g set-clipboard on
set-option -g automatic-rename on
set -s escape-time 10

# Scroll speed
bind -T copy-mode WheelUpPane send-keys -X -N 5 scroll-up
bind -T copy-mode WheelDownPane send-keys -X -N 5 scroll-down
bind -T copy-mode-vi WheelUpPane send-keys -X -N 5 scroll-up
bind -T copy-mode-vi WheelDownPane send-keys -X -N 5 scroll-down

# New window: route to repo-named session if inside a git repo
bind-key c run-shell '$HOME/.claude/bin/tmux-new-window "#{pane_current_path}"'
EOF
echo "  +   $TMUX_CONF"

# ── tmux-new-window helper ──────────────────────────────────

HELPER_DIR="$HOME/.claude/bin"
mkdir -p "$HELPER_DIR"
cat > "$HELPER_DIR/tmux-new-window" << 'EOF'
#!/usr/bin/env bash
# Create a new tmux window, routing to a repo-named session if inside a git repo.
set -euo pipefail

pane_path="$1"
repo_name=""
if cd "$pane_path" 2>/dev/null; then
  toplevel=$(git rev-parse --show-toplevel 2>/dev/null || true)
  if [[ -n "$toplevel" ]]; then
    repo_name=$(basename "$toplevel")
  fi
fi

if [[ -z "$repo_name" ]]; then
  tmux new-window
  exit 0
fi

if ! tmux has-session -t "=$repo_name" 2>/dev/null; then
  tmux new-session -d -s "$repo_name" -c "$toplevel"
else
  tmux new-window -t "=$repo_name" -c "$pane_path"
fi

tmux switch-client -t "=$repo_name"
EOF
chmod +x "$HELPER_DIR/tmux-new-window"
echo "  +   $HELPER_DIR/tmux-new-window"

# ── Shell integration (auto-attach + wrapper) ──────────────

TMUX_MARKER="# kordinate-tmux"
if ! grep -q "$TMUX_MARKER" "$SHELL_RC" 2>/dev/null; then
  cat >> "$SHELL_RC" << 'EOF'

# kordinate-tmux
# Auto-attach to 0-general on SSH login
if [ -n "$SSH_CONNECTION" ] && [ -z "$TMUX" ]; then
  tmux new-session -A -s 0-general
fi

# Bare 'tmux' attaches to 0-general; 'tmux <args>' passes through
tmux() {
  if [ $# -eq 0 ]; then
    command tmux new-session -A -s 0-general
  else
    command tmux "$@"
  fi
}
EOF
  echo "  +   Shell integration added to $SHELL_RC"
else
  echo "  ok  Shell integration already in $SHELL_RC"
fi

echo ""
echo "Done. New SSH sessions will auto-attach to tmux 0-general."
