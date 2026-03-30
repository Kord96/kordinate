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

1. **Load global preloaded files** — run the preload script for global memory:
    ```bash
    python3 $KORDINATE_HOME/team/scripts/preload.py <your-name> > /tmp/boot-<your-name>.md
    ```
    Read `/tmp/boot-<your-name>.md` with `limit: 99999` (the file can be large). Contains shared protocols and all global memory files where `preload` matches your name or `all` in KORD.json.

2. **Load project memory** — if `.kord/` exists in the current project root AND has a KORD.json:
    ```bash
    python3 $KORDINATE_HOME/team/scripts/preload.py <your-name> <project-root>/.kord > /tmp/boot-<your-name>-project.md
    ```
    Read `/tmp/boot-<your-name>-project.md` with `limit: 99999`. If `.kord/` doesn't exist, skip.

3. **Verify tools** — check that required tools are available:
    ```bash
    ast-grep --version && semgrep --version
    ```
    If either is missing, warn immediately — detection skills will not work.

4. **Check code changes** — `git log --oneline -20` for recent commits relevant to your domain.

5. **Proceed with your assigned task.**
