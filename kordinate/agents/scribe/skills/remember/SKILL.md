---
name: remember
description: Write a memory for an agent. Handles scope, frontmatter properties, kordinate and Claude native paths, and KORD.md updates.
---

Write a memory on behalf of an agent. Other agents are blocked from writing to memory/kord paths by [guard.sh](guard.sh) and told to delegate here.

$ARGUMENTS should include the agent name and what to remember.

## Procedure

1. **Classify the content**:
    - **Scratchpad** — quick observations, operational notes, things the agent noticed while working. Append to the agent's `memory/scratchpad.md`. Not curated — agents accumulate these freely.
    - **Topic file** — structured knowledge worth keeping as its own file. Create a new file in `memory/` with a descriptive name. Curated — only created or updated when explicitly requested.
    - When unclear: if it's a one-liner or transient fact, scratchpad. If it's reference material someone would look up later, topic file.

2. **Determine scope** — a single piece of information may belong in both:
    - **Global** (`$KORDINATE_HOME/agents/<name>/memory/`) — useful across projects. Cluster facts, tool patterns, general knowledge.
    - **Project** (`.kord/agents/<name>/memory/`) — specific to this repo. Local endpoints, project-specific workflows, repo-specific facts.
    - Some information belongs in both with different detail levels.

3. **Add frontmatter** — every memory file needs kordinate properties:
    ```yaml
    ---
    description: One sentence describing the content
    curated: false          # scratchpad
    scope: global           # or project
    ---
    ```
    For topic files, set `curated: true`.

4. **Write to kordinate path** — the source of truth.
    See [kordinate-recall.md](kordinate-recall.md) for paths and properties.

5. **Sync to runtime** — write to the runtime's native paths so the agent can auto-load it.
    See [claude-native.md](claude-native.md) for the current runtime's paths.

6. **Update KORD.md** — add an entry for any new file. Existing files (like scratchpad) don't need a new entry.

7. **Report** — confirm what was written, where, scope, and whether it was scratchpad or topic file.
