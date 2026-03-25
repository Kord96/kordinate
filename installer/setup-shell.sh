#!/bin/bash
# Set up shell environment: PATH, KORDINATE_HOME, tmux config.
#
# Usage: ./installer/setup-shell.sh
#
# Idempotent — safe to run repeatedly.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SHELL_RC="$HOME/.bashrc"
[ "$(uname)" = "Darwin" ] && SHELL_RC="$HOME/.zshrc"

# ── PATH + KORDINATE_HOME ───────────────────────────────────

echo "=== Shell environment ==="

MARKER="# kordinate"
if ! grep -q "$MARKER" "$SHELL_RC" 2>/dev/null; then
  cat >> "$SHELL_RC" <<EOF

$MARKER
export KORDINATE_HOME="$REPO_ROOT"
export PATH="$REPO_ROOT/bin:\$PATH"
EOF
  echo "  +   PATH + KORDINATE_HOME added to $SHELL_RC"
else
  echo "  ok  PATH already configured"
fi

# ── tmux: .tmux.conf ────────────────────────────────────────

echo ""
echo "=== tmux ==="

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

# ── tmux: new-window helper ─────────────────────────────────

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

# ── tmux: shell integration (auto-attach + wrapper) ─────────

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
echo "Done."

# ── git-crypt: worktree compatibility ───────────────────────

echo ""
echo "=== git-crypt worktree fix ==="

# git-crypt stores its key under .git/git-crypt/keys/ which is only
# accessible from the main working tree. Worktrees set GIT_DIR to
# .git/worktrees/<name>/ so git-crypt cannot find the key and the
# smudge filter fails. These wrappers redirect GIT_DIR to the common
# dir (--git-common-dir) so worktree checkouts decrypt correctly.

REPO_GIT_DIR="$REPO_ROOT/.git"

if [ -d "$REPO_GIT_DIR/git-crypt" ]; then
  cat > "$REPO_GIT_DIR/git-crypt-smudge-wrapper.sh" << 'EOF'
#!/bin/bash
export GIT_DIR="$(git rev-parse --git-common-dir 2>/dev/null || git rev-parse --git-dir)"
exec git-crypt smudge "$@"
EOF

  cat > "$REPO_GIT_DIR/git-crypt-clean-wrapper.sh" << 'EOF'
#!/bin/bash
export GIT_DIR="$(git rev-parse --git-common-dir 2>/dev/null || git rev-parse --git-dir)"
exec git-crypt clean "$@"
EOF

  chmod +x "$REPO_GIT_DIR/git-crypt-smudge-wrapper.sh" "$REPO_GIT_DIR/git-crypt-clean-wrapper.sh"
  git -C "$REPO_ROOT" config filter.git-crypt.smudge "\"$REPO_GIT_DIR/git-crypt-smudge-wrapper.sh\""
  git -C "$REPO_ROOT" config filter.git-crypt.clean "\"$REPO_GIT_DIR/git-crypt-clean-wrapper.sh\""
  echo "  +   git-crypt worktree wrappers installed"
else
  echo "  ok  git-crypt not initialized — skipping"
fi
