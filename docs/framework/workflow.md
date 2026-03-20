# Workflow

How you interact with kordinate day-to-day.

## Overview

```mermaid
flowchart LR
    U([You]) -->|SSH| WP

    subgraph WP[Workstation]
        T[tmux] --> CC[Claude Code]
        CC --> AG[Agents]
        AG <-->|every tool call| HK[Hooks]
    end
```

Each tmux window runs its own Claude Code instance with isolated agents and hooks.

## Worktree Sessions

Each window creates an isolated git worktree + branch via `bin/claude-session`. On exit: push + PR if changes, cleanup if not.

```mermaid
flowchart TB
    subgraph tmux
        direction TB
        subgraph ks[kordinate session]
            W0[window 0 — main branch<br/>no worktree]
            W1[window 1 — session/w1-kordinate<br/>isolated worktree]
            W2[window 2 — session/w2-kordinate<br/>isolated worktree]
        end
        subgraph ps[your-project session]
            PW0[window 0 — main branch]
            PW1[window 1 — session/w1-project<br/>isolated worktree]
        end
    end

    W1 & W2 & PW1 -->|on exit| PR{changes?}
    PR -->|yes| PUSH[push + create PR]
    PR -->|no| CLEAN[cleanup worktree]
    PUSH --> FF{fast-forward main?}
    FF -->|yes| CLOSE[close PR]
    FF -->|no| MERGE[run /merge]
```

## Branch Model

`session/*` → `main` → `test` → `prod`

The `auto-merge-to-dev.sh` hook tries to fast-forward main after each push to a session branch. If it fails (conflicts), run `/merge`.
