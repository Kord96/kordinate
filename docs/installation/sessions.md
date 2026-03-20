# Sessions & Branches

Each tmux window runs its own agent runtime with isolated agents and hooks. Windows create isolated git worktrees + branches via `bin/claude-session`. On exit: push + PR if changes, cleanup if not.

```mermaid
flowchart TB
    subgraph tmux
        direction TB
        subgraph p1[project-1 session]
            W0[window 0 — main branch<br/>no worktree]
            W1[window 1 — session/w1<br/>isolated worktree]
            W2[window 2 — session/w2<br/>isolated worktree]
        end
        subgraph p2[project-2 session]
            PW0[window 0 — main branch]
            PW1[window 1 — session/w1<br/>isolated worktree]
        end
    end

    W1 & W2 & PW1 -->|on exit| PR{changes?}
    PR -->|yes| PUSH[auto-push + PR created]
    PR -->|no| CLEAN[cleanup worktree]
    PUSH --> FF{conflicts?}
    FF -->|no| CLOSE[merged to main, PR closed]
    FF -->|yes| MERGE[/merge triggered]
```

## Branch Model

`session/*` → `main` → `test` → `prod`

The `auto-merge-to-dev.sh` hook tries to fast-forward main after each push. If it fails, run `/merge`.
