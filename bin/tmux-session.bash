# Tmux session management for .bashrc
# Source this file to get organized tmux sessions.
#
# Features:
# - Generates ~/.tmux.conf on first source
# - Auto-attach to default session on SSH login
# - Bare `tmux` command attaches to default (instead of creating new sessions)
# - New windows route to repo-named sessions (via tmux-new-window)

_tmux_bin_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Skip everything in non-interactive shells (subagent Bash tool calls)
[[ $- != *i* ]] && return 2>/dev/null

# ─── Generate tmux.conf if missing ───
if [ ! -f "$HOME/.tmux.conf" ]; then
  cat > "$HOME/.tmux.conf" <<TMUXCONF
set -g mouse on
set -g set-clipboard on
set-option -g automatic-rename on
bind-key c run-shell '$_tmux_bin_dir/tmux-new-window "#{pane_current_path}"'
TMUXCONF
fi

# ─── Save layout on session/window structural changes ───
# Only in interactive shells — subagent Bash calls inherit $TMUX and would
# re-register hooks on every tool call, causing session conflicts.
if [ -n "${TMUX:-}" ] && [ -x "$_tmux_bin_dir/tmux-save" ] && [[ $- == *i* ]]; then
  command tmux set-hook -g after-new-session "run-shell '$_tmux_bin_dir/tmux-save 2>/dev/null || true'" 2>/dev/null || true
  command tmux set-hook -g after-new-window "run-shell '$_tmux_bin_dir/tmux-save 2>/dev/null || true'" 2>/dev/null || true
  command tmux set-hook -g session-closed "run-shell '$_tmux_bin_dir/tmux-save 2>/dev/null || true'" 2>/dev/null || true
fi

# ─── Default session ───
TMUX_DEFAULT="0-general"

# Rename bare '0' session to default if it slipped through
if command tmux has-session -t 0 2>/dev/null && ! command tmux has-session -t "$TMUX_DEFAULT" 2>/dev/null; then
  command tmux rename-session -t 0 "$TMUX_DEFAULT"
fi

# Auto-attach to default tmux session on SSH login
if [[ -n "$SSH_CONNECTION" ]] && [[ -z "$TMUX" ]] && [[ $- == *i* ]]; then
  command tmux select-window -t "$TMUX_DEFAULT:0" 2>/dev/null
  tmux attach-session -t "$TMUX_DEFAULT" 2>/dev/null || tmux new-session -s "$TMUX_DEFAULT"
fi

# tmux: attach to default session when no args
tmux() {
  if [[ $# -eq 0 ]]; then
    command tmux has-session -t "$TMUX_DEFAULT" 2>/dev/null || command tmux new-session -d -s "$TMUX_DEFAULT"
    command tmux attach-session -t "$TMUX_DEFAULT"
  else
    command tmux "$@"
  fi
}
