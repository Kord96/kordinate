---
name: boot
description: Load memory and shared protocols on spawn. Run before starting any task.
curated: true
scope: global
---

Load your context before starting work.

## Steps

1. **Read shared protocols** — read all files in `$KORDINATE_HOME/shared/`. These are team-wide instructions.

2. **Read your memory** — load both scopes:
    - Global: `$KORDINATE_HOME/agents/<your-name>/memory/`
    - Project: `.kord/agents/<your-name>/memory/` (if it exists)

3. **Check code changes** — `git log --oneline -20` for recent commits relevant to your domain.

4. **Proceed with your assigned task.**
