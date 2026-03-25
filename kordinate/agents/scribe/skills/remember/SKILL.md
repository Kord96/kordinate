---
name: remember
description: Write a memory for an agent. Decides global vs project scope, writes to kordinate and Claude native paths, updates KORD.md.
---

Write a memory on behalf of an agent. $ARGUMENTS should include the agent name and what to remember.

## Procedure

1. **Analyze the content** — a single piece of information may contain both global and project-specific parts. Split if needed:
    - Cluster facts, tool patterns, cross-project knowledge → **global**
    - References to specific repos, project files, local endpoints → **project**
    - Some information belongs in both scopes with different detail levels (e.g. "DNS issues with .local domains" is global, "logbd service at 10.0.1.5 affected" is project)
    - When unclear, ask.

2. **Determine paths** — for each scope, write to both kordinate and Claude native paths.
    See [kordinate-recall.md](kordinate-recall.md) for kordinate paths and properties.
    See [claude-native.md](claude-native.md) for Claude Code paths and behaviors.

3. **Write the memory files** — create or update topic files in the agent's memory directory.
    - Use descriptive filenames (e.g. `dns-patterns.md`, `cluster-topology.md`)
    - If the topic already exists, append or update — don't overwrite
    - A single request may produce files in both global and project scope

4. **Update KORD.md** — add entries for any new files.

5. **Report** — confirm what was written, where, and the scope(s) chosen.
