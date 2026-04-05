---
name: publish
description: Push the current branch explicitly and optionally prepare it for review. Does not update main.
argument-hint: "[--draft-pr] [--codex-review]"
curated: true
scope: global
---

Publish the current branch without mutating `main`.

`$ARGUMENTS` flags:
- `--draft-pr` — after pushing, prepare or create a draft PR
- `--codex-review` — if used with `--draft-pr`, mention/request Codex review in the PR flow

## Rules

- Never update `main` from this skill.
- Always fetch first so ahead/behind status is current.
- If on `main`, stop and tell the user to use a session branch/worktree instead.
- Keep PR creation optional; pushing a branch is the default action.

## Procedure

1. `git fetch --all --prune || true`
2. Show branch, dirty state, and ahead/behind status.
3. If working tree is dirty, stop and ask the user to commit first.
4. Push the current branch to origin.
5. If `--draft-pr` is passed, prepare or create a draft PR.
6. If `--codex-review` is also passed, include the requested Codex review trigger in the PR flow.
7. Report the published branch and any review/PR artifacts created.

## Output

Keep output brief. Emphasize that `main` was not changed.