---
name: boot
description: Load memory and shared protocols on spawn. Run before starting any task.
---

Load your context before starting work.

Your agent name is the `name` field from your own frontmatter. Use it wherever `<your-name>` appears below.

## Steps

0. **Sync kord state** — if `$KORDINATE_HOME` is a git repo with a remote configured (`git -C "$KORDINATE_HOME" remote` returns output), pull:
    ```bash
    git -C "$KORDINATE_HOME" pull --ff-only 2>/dev/null || true
    ```
    Skip if no remote is configured.

1. **Load preloaded files** — run the preload script to get all files marked for you in one read:
    ```bash
    python3 $KORDINATE_HOME/team/scripts/preload.py <your-name> > /tmp/boot-<your-name>.md
    ```
    Read `/tmp/boot-<your-name>.md`. This contains shared protocols and all memory files where `preload` matches your name or `all` in KORD.json. Faster than scanning frontmatter.

2. **Check code changes** — `git log --oneline -20` for recent commits relevant to your domain.

3. **Proceed with your assigned task.**
