---
name: remember
description: Write a memory for an agent. Decides global vs project scope, writes to kordinate and Claude native paths, updates KORD.md.
---

Write a memory on behalf of an agent. $ARGUMENTS should include the agent name and what to remember.

## Procedure

1. **Determine scope** — is this useful across projects or specific to this one?
    - References to specific repos, project files, local endpoints → **project**
    - Cluster facts, tool patterns, cross-project knowledge → **global**
    - When unclear, ask.

2. **Determine paths** — based on scope, write to both kordinate and Claude native paths.
    See [kordinate-recall.md](kordinate-recall.md) for kordinate paths and properties.
    See [claude-native.md](claude-native.md) for Claude Code paths and behaviors.

3. **Write the memory file** — create or update a topic file in the agent's memory directory.
    - Use a descriptive filename (e.g. `dns-patterns.md`, `cluster-topology.md`)
    - If the topic already exists, append or update — don't overwrite

4. **Update KORD.md** — add an entry for the new file if it's new.

5. **Report** — confirm what was written, where, and the scope chosen.
