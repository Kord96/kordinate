---
description: /architect skill must produce hierarchical architecture data for the Cytoscape viewer, not flat component inventories
curated: true
scope: global
---
# /architect Cytoscape Hierarchy Requirements

The /architect skill produces architecture YAML consumed by the Cytoscape graph viewer. The output must be **hierarchical**, not flat.

## Key requirements

1. **Abstract group nodes** -- create organizational containers that emerge from the project's natural structure. Every component must have a `parent`. Root groups should be few — the number depends on the project architecture, not a hardcoded count.
2. **`hasChildren: true`** on all group nodes.
3. **Sparse edges** -- ~15-20 meaningful data flows, not 90+ import relationships. Only semantically meaningful flows (SSR prefetch, cart flow, theme toggle, etc.).
4. **Hierarchy enables expand/collapse** in the Cytoscape viewer. Flat data makes the graph crowded and unusable.

## Evidence

| Metric | Hand-crafted (sous-storefront) | Agent-produced |
|--------|-------------------------------|----------------|
| Root groups | 3 | 15 |
| Total groups | 22 | 12 |
| Total nodes | 62 | 57 |
| Edges | 17 | 93 |
| Result | Clean, navigable | Too flat, noisy, unusable |

The agent version had too many roots (15 vs 3) and too few groups (12 vs 22), meaning components were not nested into a useful hierarchy. The edge count (93 vs 17) shows every import was included rather than curating meaningful data flows.

## YAML structure

Group nodes must be defined explicitly with `hasChildren: true`:

```yaml
components:
  - id: server
    name: Server
    type: group
    hasChildren: true
  - id: ssr-server
    name: SSR Server
    type: service
    hasChildren: true
    parent: server
  - id: vite-config
    name: Vite Config
    type: config
    parent: ssr-server
    file: vite.config.ts
```

## Rules of thumb

- **Roots**: few top-level groups that emerge from the project's architecture. The number is project-dependent, not hardcoded.
- **Nesting**: every leaf component must be nested under a group. Create abstract containers to organize related components — modules, layers, features, domains.
- **Edges**: only data flows that a developer would draw on a whiteboard. Skip internal imports, utility references, type-only dependencies.
- **Test**: if a node has no parent, it must be an intentional root group. If there are more parentless nodes than natural architectural layers, the hierarchy is too flat.
