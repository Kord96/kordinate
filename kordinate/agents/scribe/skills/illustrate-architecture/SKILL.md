---
name: illustrate-architecture
description: Transform a project's architecture into interactive viewer JSON — reads architecture.yaml for structure, reads the code for flows and state.
curated: true
scope: global
---

Transform a project's architecture into viewer-ready JSON for the ProjectExplorer component.

## Arguments

`$ARGUMENTS` — Required: `<project>`. Optional: `--tutorial`.

The project must have an `architecture.yaml` at `<project>/.claude/agent-memory/designer/architecture.yaml`. If not, suggest running `/designer:architect` first.

## Inputs

Two inputs, each with a different purpose:

1. **architecture.yaml** — the structural map. Use it for: component hierarchy, root groups, `depends_on` edges, external dependencies. The architect already did the hard work of identifying what the pieces are.

2. **The project source code** — the execution truth. Read the actual code to trace flows, understand state management, and identify failure cascades. The architecture.yaml's `data_flows` are a starting point, but they're often too shallow. The code tells you what actually happens.

## Procedure

### Structure (from architecture.yaml)

1. Run [convert-to-viewer.py](convert-to-viewer.py) to produce the initial JSON from the YAML:
   ```bash
   python3 convert-to-viewer.py <architecture.yaml> <output.json>
   ```
   This handles: hierarchy flattening, `depends_on` edges, flow edges, dedup, bidirectional label hiding.

2. Review the structure: root groups make sense, no orphans, clean hierarchy.

### Flows (from the code)

3. For each `data_flow` in architecture.yaml, **read the actual source files** involved and trace the full reactive chain. The YAML gives you the starting point (which components participate), but you must follow the execution through the code to produce rich sequence diagrams.

   Each flow must include:
   - **All participants**, not just components — include infrastructure (SSR server, browser), APIs (IntersectionObserver, DOM), stores, and the user
   - **5-12 steps** tracing the complete path from trigger to user-visible outcome
   - **Reactive propagation** — store updates → subscribers re-render → side effects fire
   - **Serialization boundaries** — where data crosses process/format boundaries
   - **Domain-specific details** — pagination params, delay values, cache keys, guard conditions

   Write the flow data into the `data_flows` array in the JSON. Each flow needs:
   - `id`, `name`, `description`, `trigger`
   - `steps` with `component`, `action`, `data`, `to`, `technology`
   - `mermaid` — a complete Mermaid sequence diagram string for the Flows tab

   The `mermaid` field is the primary visualization. The `steps` are metadata. Put the effort into making the Mermaid diagram clear and detailed.

### State (from architecture.yaml + code)

4. For the Data tab, include `state` entries from architecture.yaml. If they're thin, read the actual store/cache implementations to identify readers and writers.

### Failure Modes (from architecture.yaml + code)

5. For the Resilience tab, include `failure_modes` from architecture.yaml. If cascade chains are shallow, trace through the code to understand the actual blast radius.

### Tutorial (if --tutorial)

6. Produce a brief walkthrough: what is this, who uses it, how does it work (one section per flow as narrative), what's stored where, what can go wrong.

### Write output

7. Write `architecture.json` to the docs site content directory. Write tutorial if requested.

8. **Report** — node count, edge count, root groups, flow step counts, which tabs have content.
