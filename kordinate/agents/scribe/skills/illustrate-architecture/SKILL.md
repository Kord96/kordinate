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

2. **patterns.md** (optional) — from `/detect-patterns`. Which patterns the code uses, anti-patterns present, and patterns MISSING.

3. **The project source code** — the execution truth. Always read the code.

## Procedure

### 1. Read everything

Read architecture.yaml to understand the structure. Read patterns.md if it exists. Then use `modules` fields from the YAML to find key source files and read them. Build a unified understanding of how the system works before producing anything.

### 2. Produce the viewer JSON in one pass

Produce `architecture.json` directly from your understanding. Don't use intermediate tools or converters — produce the complete JSON yourself. The output shape:

```json
{
  "nodes": [...],
  "edges": [...],
  "state": [...],
  "failure_modes": [...],
  "data_flows": [...]
}
```

All viewpoints are different lenses on the same understanding. Produce them together — a flow reveals state dependencies, state reveals failure cascades, failures reveal missing resilience in flows.

**Nodes** — from `components` + `children` in the YAML:
- Walk recursively. Components with children → `type: "group"`, `hasChildren: true`
- Leaf types: frontend→component, store→library, api/worker→service, gateway→external-service
- `parent` from nesting. Top-level components have no parent.
- `file` from `modules[0]`. `exports` if available.
- Add `external_dependencies` as nodes under an "External" group.
- Review: merge single-child root groups into neighbors. Prune root groups with no edges.

**Edges** — from `depends_on` + `data_flows`:
- Flow edges from flow steps (label with flow name, set `flowId`)
- Structural edges from `depends_on` (label "uses", `flowId: "dependency"`)
- Skip dependency edges if a flow edge already connects the same pair
- Bidirectional flows: keep both arrows, set `hideLabel: true` on the return edge
- No render edges — containment communicates parent-child relationships

**Flows** — trace each data flow through the CODE (not just the YAML steps):
- Include all participants: users, components, stores, browser APIs, framework internals
- 5-12 steps per flow, ending at the user-visible outcome
- Domain details: pagination params, delays, cache keys, guard conditions
- Write a `mermaid` sequence diagram string for each flow (`sequenceDiagram` format with `participant` declarations, `->>` arrows, `Note over` annotations)
- If patterns.md reports anti-patterns in a flow path, annotate them

**State** — for each store/cache:
- Search the code for imports/usage of the store hook to find all readers and writers
- Include: persistence mechanism, serialization, scope

**Failure modes** — for each failure:
- Trace the cascade through the code
- If patterns.md reports missing resilience (no timeout, no retry), surface prominently

### 3. Write output

Write `architecture.json` to the docs site content directory for the project.

### 4. Tutorial (if --tutorial)

What is this, who uses it, how does it work (one section per flow), what's stored where, what can go wrong.

### 5. Report

Node count, edge count, root groups, flow step counts (target: average 8+), state reader/writer counts.

## Reference

[convert-to-viewer.py](convert-to-viewer.py) documents the mechanical conversion rules (hierarchy flattening, edge dedup, bidirectional handling). Use it as a reference for the JSON format, not as a required step.
