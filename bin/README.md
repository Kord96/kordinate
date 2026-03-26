# bin

CLI utilities for session and tmux management.

| Script | Purpose |
|--------|---------|
| [claude-session](claude-session) | Worktree-based session launcher — creates `session/w<N>-<repo>` branches, auto-resumes, commits on exit |
| [tmux-new-window](tmux-new-window) | Routes new tmux windows to repo-named sessions |
| [tmux-save](tmux-save) | Saves tmux session layout to persistent storage (periodic + preStop) |
| [tmux-restore](tmux-restore) | Restores tmux sessions/windows from saved layout at boot |
| [tmux-session.bash](tmux-session.bash) | Shell integration — auto-attach to `0-general` session on SSH |
