---
name: illustrate-architecture
description: Transform a project's architecture.yaml into an interactive viewer JSON and optional tutorial — the primary visual documentation output.
curated: true
scope: global
---

Transform a project's architectural understanding into viewer-ready JSON for the ProjectExplorer component, and optionally a brief tutorial.

## Arguments

`$ARGUMENTS` — Required: `<project>` (e.g., `logbd`, `stoik`, `sous-storefront`). Optional: `--tutorial` to also generate a brief tutorial.

The project must have an `architecture.yaml` at `<project>/.claude/agent-memory/designer/architecture.yaml`. If it doesn't exist, report and suggest running `/designer:architect` first.

## Procedure

1. Parse project name from `$ARGUMENTS`. Locate the project directory.

2. **Read architecture.yaml** — this is the sole input. Understand the component hierarchy, flows, state, and failure modes.

3. **Produce viewer JSON** — convert the architecture into `architecture.json` for the ProjectExplorer Cytoscape viewer. The JSON has this shape:

   ```json
   {
     "nodes": [...],
     "edges": [...],
     "state": [...],
     "failure_modes": [...],
     "data_flows": [...]
   }
   ```

   ### Nodes

   Walk the `components` array recursively (including `children`). For each component, create a node:
   - `id`, `name`, `description` — from the component
   - `type` — `"group"` if it has children. Otherwise map: frontend→component, store→library, api/worker→service, gateway→external-service
   - `hasChildren` — true if it has a `children` array
   - `parent` — the parent component's id (from nesting). Top-level components have no parent.
   - `file` — from `modules[0]` if available
   - `exports` — if available

   Also add `external_dependencies` as nodes with type `"external-service"`. Create an "External" group if one doesn't already exist.

   ### Edges

   Three sources of edges, in priority order:

   **Flow edges** (highest priority) — from `data_flows`. For each flow, create edges between consecutive steps. Label with the flow name, set `flowId` to the flow id.

   **Structural edges** — from `depends_on` on components. Label as "uses", set `flowId` to "dependency". Skip if a flow edge already connects the same pair of nodes.

   **Do NOT add render edges** — children nested inside group nodes are visually connected by the containment itself. Adding parent→child "renders" edges creates long crossing arrows that clutter the graph. Leaf nodes without explicit edges are fine — their position inside a group communicates the relationship.

   ### State, Failure Modes, Data Flows

   Include `state`, `failure_modes`, and `data_flows` from the architecture.yaml directly in the JSON. These populate the Data, Resilience, and Flows tabs respectively.

   A reference implementation of this conversion is at [convert-to-viewer.py](convert-to-viewer.py). You can run it for validation, but you should produce the JSON yourself using your judgment — the script is a fallback, not a replacement for understanding the architecture.

4. **Review the output** — before writing, check:
   - Are there orphan leaf nodes with no edges? Fix them.
   - Are there duplicate edges (same pair connected by both flow and dependency)? Remove the dependency.
   - Do the root groups make sense? If there are more than 5 root nodes, consider whether some should be grouped.
   - Are the flow edges telling a coherent story? Each flow should trace a clear path through the system.

5. **Generate tutorial** (if `--tutorial` flag) — produce a brief walkthrough:
   - **What is this?** — from `purpose` + `stack`
   - **Who uses it?** — from `actors`
   - **How does it work?** — one section per `data_flow`, narrative walkthrough referencing components by name
   - **What's stored where?** — from `state`, grouped by purpose
   - **What can go wrong?** — from `failure_modes`, ordered by severity

   Write in plain language. No code snippets. The goal is "understand the system in 5 minutes."

6. **Write output** — write `architecture.json` to the docs site content directory for the project (e.g., `docs/src/content/docs/<project>/architecture.json`). Write tutorial to `<project>/.claude/agent-memory/scribe/tutorial.md` if requested.

7. **Report** — node count, edge count, root groups, orphan count (should be 0), which tabs have content.
