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

2. **Read your memory** — load both scopes, reading all `.md` files recursively (some agents have subdirectories):
    - Global: `$KORDINATE_HOME/agents/<your-name>/memory/`
    - Project: `<project-root>/.kord/agents/<your-name>/memory/` — relative to the current working directory. Skip if the `.kord/` directory does not exist in the project root.

3. **Check code changes** — `git log --oneline -20` for recent commits relevant to your domain.

4. **Proceed with your assigned task.**
