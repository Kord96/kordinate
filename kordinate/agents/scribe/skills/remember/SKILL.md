---
name: remember
description: Write a memory for an agent. Handles scope, frontmatter properties, kordinate and Claude native paths, and KORD.md updates.
curated: true
scope: global
---

Write a memory on behalf of an agent. Other agents are blocked from writing to memory/kord paths by [guard.sh](guard.sh) and told to delegate here.

$ARGUMENTS should include the agent name and what to remember.

**Important**: This skill writes to kordinate paths (source of truth) and updates the runtime index. It does NOT write to Claude's main session auto memory (`~/.claude/projects/<project>/memory/`) — that is managed by Claude itself.

## Procedure

1. **Classify content** — run `/sanitize` first. It separates config, credentials, and memory. Only memory proceeds here.

2. **Classify memory type**:
    - **Scratchpad** — quick observations, operational notes, things the agent noticed while working. Append to the agent's `memory/scratchpad.md`. Not curated — agents accumulate these freely.
    - **Topic file** — structured knowledge worth keeping as its own file. Create a new file in `memory/` with a descriptive name. Curated — only created or updated when explicitly requested.
    - When unclear: if it's a one-liner or transient fact, scratchpad. If it's reference material someone would look up later, topic file.

3. **Determine scope** — a single piece of information may belong in both:
    - **Global** (`$KORDINATE_HOME/agents/<name>/memory/`) — useful across projects. Cluster facts, tool patterns, general knowledge.
    - **Project** (`.kord/agents/<name>/memory/`) — specific to this repo. Local endpoints, project-specific workflows, repo-specific facts.
    - Some information belongs in both with different detail levels.

4. **Add frontmatter** — every memory file needs kordinate properties:
    ```yaml
    ---
    description: One sentence describing the content
    curated: false          # scratchpad
    scope: global           # or project
    ---
    ```
    For topic files, set `curated: true`.

5. **Write to kordinate path** — the source of truth.
    See [kordinate-recall.md](kordinate-recall.md) for paths and properties.

6. **Update runtime index** — update the agent's `MEMORY.md` in the runtime so it appears on next spawn.

    How Claude's subagent memory works: `~/.claude/agent-memory/<name>/MEMORY.md` is auto-loaded (first 200 lines) when the subagent spawns. It is a **single flat file** — no topic files, no auto-discovery of linked files. The `/boot` skill reads the full kordinate memory later, but MEMORY.md gives the agent immediate awareness of what it knows.

    Rules:
    - **New topic file** → add one index line to MEMORY.md: `- [filename.md](<absolute-kordinate-path>) — description`
    - **Scratchpad append** → no MEMORY.md change needed (scratchpad entry already in index)
    - **Global scope** → update `~/.claude/agent-memory/<name>/MEMORY.md`
    - **Project scope** → update `.claude/agent-memory/<name>/MEMORY.md` (create dir if needed)
    - **200-line limit** — check line count after adding. If over, remove the least relevant entries (the files still exist in kordinate — only the index preview is trimmed)
    - **Never copy full content** into MEMORY.md — it is an index of pointers, not a knowledge base

7. **Regenerate KORD.md** — run [generate-kord.sh](generate-kord.sh) to rebuild the index from frontmatter. Never edit KORD.md manually.

8. **Report** — confirm what was written, where, scope, and whether it was scratchpad or topic file.
