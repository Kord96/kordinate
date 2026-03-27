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

1. **architecture.yaml** — the structural map. Component hierarchy, root groups, `depends_on` edges. Your guide to what the pieces are.

2. **patterns.md** (optional) — from `/detect-patterns`. Which patterns the code uses, anti-patterns present, and patterns MISSING. Enriches every viewpoint.

3. **The project source code** — the execution truth. Always read the code.

## Procedure

### 1. Structure

Run [convert-to-viewer.py](convert-to-viewer.py) to produce the initial JSON. If the script isn't available, produce the structure manually: walk `components` + `children` → flat nodes with parent/hasChildren, extract `depends_on` → edges, add externals.

Review the structure:
- Merge root groups with only 1 child into a neighbor
- Prune root groups with no edges to other groups
- Merge related thin groups into one

### 2. Read the code

Use `modules` fields from architecture.yaml to find the key files. Read them. Build a unified understanding of how the system works before producing any viewpoints.

If `patterns.md` exists, read it too — note which components have patterns, which have anti-patterns, and what's missing.

### 3. Produce all viewpoints at once

Each viewpoint is a lens on the same understanding:

**Flows** — trace each data flow through the code as a full reactive chain:
- Include all participants: users, components, stores, browser APIs (IntersectionObserver, localStorage, DOM), framework internals (HydrationBoundary, QueryClient)
- 5-12 steps per flow, ending at the user-visible outcome
- Include domain details: pagination params, delays, cache keys, guard conditions
- Write a `mermaid` sequence diagram string for each flow (the Flows tab renders these)
- Mermaid format: `sequenceDiagram` with `participant` declarations, `->>`/`-->>` arrows, `Note over` annotations
- If patterns.md reports anti-patterns in a flow path, annotate them

**State** — for each store/cache:
- Search the code for every import/usage of the store hook to find all readers and writers
- Include: persistence mechanism, serialization format, scope (per-request vs singleton vs global)
- If patterns.md reports state-related patterns (reactive-store, cache-aside), note them

**Failure modes** — for each failure:
- Trace the cascade through the code: what breaks first, what breaks next, what the user sees
- Include detection signals and recovery steps
- If patterns.md reports missing resilience patterns (no timeout, no retry), surface these prominently

These inform each other. Produce them together.

### 4. Write output

Merge the structure with enriched viewpoints into `architecture.json`:
```json
{
  "nodes": [...],
  "edges": [...],
  "state": [...],
  "failure_modes": [...],
  "data_flows": [...]
}
```

Write to the docs site content directory.

### 5. Tutorial (if --tutorial)

What is this, who uses it, how does it work (one section per flow), what's stored where, what can go wrong.

### 6. Report

Node count, edge count, root groups, flow step counts (target: average 8+), state reader/writer counts.
