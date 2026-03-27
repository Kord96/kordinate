---
name: illustrate-architecture
description: Transform a project's architecture into interactive viewer JSON — reads architecture.yaml for structure, reads the code for all viewpoints.
curated: true
scope: global
---

Transform a project's architecture into viewer-ready JSON for the ProjectExplorer component.

## Arguments

`$ARGUMENTS` — Required: `<project>`. Optional: `--tutorial`.

The project must have an `architecture.yaml` at `<project>/.claude/agent-memory/designer/architecture.yaml`. If not, suggest running `/designer:architect` first.

## Inputs

Three inputs, each with a different purpose:

1. **architecture.yaml** — the structural map. Component hierarchy, root groups, `depends_on` edges, external dependencies. Your guide to what the pieces are.

2. **patterns.md** (optional) — from `/detect-patterns`. Tells you which patterns the code uses (reactive-store, circuit-breaker, etc.), which anti-patterns exist (swallowed exceptions, n+1 queries), and which patterns are MISSING (no timeout, no retry). Use this to enrich every viewpoint — tag components with their patterns, highlight anti-patterns as warnings, and surface gaps prominently in the Resilience tab.

3. **The project source code** — the execution truth. Always read the code. The YAML is a map, patterns.md is annotations, the code is the territory.

## Procedure

1. **Run the converter** to produce the initial structural JSON from the YAML:
   ```bash
   python3 convert-to-viewer.py <architecture.yaml> <output.json>
   ```
   This gives you nodes, hierarchy edges, and a skeleton. The structure is done.

2. **Review the structure.** Check the converter output: prune root groups that have no edges to other groups (testing, CI/CD, build tooling rarely help someone understand how the system works — remove them). Then read the codebase. Use architecture.yaml to know which files matter, then read them. Build a unified understanding — don't think about tabs yet. Just understand the code.

3. **Produce all viewpoints at once** from that understanding. Each viewpoint is a different lens on the same codebase:

   **Flows** — for each data flow, trace the full reactive chain through the code. Include all participants (not just components — users, browser APIs, DOM, framework internals). 5-12 steps per flow. End at the user-visible outcome. Write a `mermaid` sequence diagram string for each flow. Short labels, detailed `action` fields.

   **State** — for each store/cache, identify every component that reads from it and every component that writes to it by searching the code for usage. Include persistence mechanism and serialization format.

   **Failure modes** — for each failure, trace the cascade through the code. Which components break, in what order, what does the user see, how is it detected, how does it recover.

   These inform each other. A flow reveals state dependencies. State reveals failure cascades. Failure reveals missing resilience in flows. Produce them together.

4. **Write the enriched JSON** — merge the converter's structural output with your enriched flows, state, and failure data. The JSON shape:
   ```json
   {
     "nodes": [...],
     "edges": [...],
     "state": [...],
     "failure_modes": [...],
     "data_flows": [...]
   }
   ```

5. **Generate tutorial** (if `--tutorial`) — what is this, who uses it, how does it work (one section per flow), what's stored where, what can go wrong.

6. **Write output** — `architecture.json` to the docs site. Tutorial if requested.

7. **Report** — node count, edge count, root groups, flow step counts (should average 8+), state reader/writer counts.
