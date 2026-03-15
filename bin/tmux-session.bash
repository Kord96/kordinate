# Tmux session management for .bashrc
# Source this file from your .bashrc to get organized tmux sessions.
#
# Features:
# - Auto-attach to default session on SSH login
# - Bare `tmux` command attaches to default (instead of creating new sessions)
# - Windows auto-rename to current directory name
#
# Session registry lives in tmux-sessions.conf

_tmux_conf_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${_tmux_conf_dir}/tmux-sessions.conf"

# Build default session name from registry (index-name)
_tmux_default_entry="${TMUX_SESSIONS[0]}"
TMUX_DEFAULT="${_tmux_default_entry%%:*}-${_tmux_default_entry##*:}"

# Rename bare '0' session to default if it slipped through
if command tmux has-session -t 0 2>/dev/null && ! command tmux has-session -t "$TMUX_DEFAULT" 2>/dev/null; then
    command tmux rename-session -t 0 "$TMUX_DEFAULT"
fi

# Auto-attach to default tmux session on SSH login
if [[ -n "$SSH_CONNECTION" ]] && [[ -z "$TMUX" ]] && [[ $- == *i* ]]; then
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

