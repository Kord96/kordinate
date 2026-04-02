---
name: boot
description: Load memory and shared protocols on spawn. Run before starting any task.
curated: true
scope: global
---

Load your context before starting work.

Your agent name is the `name` field from your own frontmatter. Use it wherever `<your-name>` appears below.

## Steps

0. **Sync kord state** — if `$KORDINATE_HOME` is a git repo with a remote configured (`git -C "$KORDINATE_HOME" remote` returns output), pull memory written by Beorn agents since the last session:
    ```bash
    git -C "$KORDINATE_HOME" pull --ff-only 2>/dev/null || true
    ```
    This only applies to local workstations — the PVC is already current on-cluster. If no remote is configured, skip.

1. **Read shared protocols** — read all files in `$KORDINATE_HOME/shared/` (memory-protocol.md, auth-protocol.md, credentials-protocol.md). These are team-wide instructions.

2. **Read your memory** — load files marked for you:
    - Global: in `memory/global/` (relative to your agent dir, loaded via CLAUDE.md), read files
      where frontmatter has `preloaded: <your-name>` or `preloaded: all`.
      Skip files with `preloaded: none` (they're available on demand).
    - Project: at `$MEM/` (injected per-job by the runner).
      Skip if `$MEM` is not set.
    - Files without a `preloaded` property default to `none` (not loaded).

3. **Check code changes** — `git log --oneline -20` for recent commits relevant to your domain.

4. **Proceed with your assigned task.**
