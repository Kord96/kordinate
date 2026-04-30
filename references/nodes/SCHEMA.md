---
schema: node-system.v1
---

# Node System Schema

This directory uses one schema version: `node-system.v1`. The same version
applies to `NODE.md`, node module output, shared helpers, and validator docs in
this node system.

## Node Directory

Each implemented node lives at `nodes/<node-id>/`:

```text
nodes/<node-id>/
  NODE.md
  module/
    main.py
```

`NODE.md` is the semantic document. Its frontmatter is the node metadata; do not
duplicate that metadata in a separate semantics file or in the body.

## NODE.md

```yaml
---
schema: node-system.v1
node_id: <stable kebab-case id matching the directory name>
name: <short human-readable name>
summary: <one sentence describing the node>
detection_style: <deterministic | semantic | composite>
detection_effort: <none | low | medium | high; high means semantic detection needs a strong model>
abstraction_level: [<0-100 lower bound>, <0-100 upper bound>]
edges:
  - target: <node-id this node relates to>
    relation: <requires | supports | refines | conflicts_with | reuses | emits>
    strength: <weak | medium | strong>
    confidence_effect: <required | increases | decreases | contextual>
---
```

Required body sections:

```md
## Boundary

## Positive Evidence

## Rejections

## Edge Semantics

## Module Checks
```

`## Boundary` states what the node includes and excludes.
`## Positive Evidence` states what evidence should activate the node.
`## Rejections` states what similar evidence must not activate the node.
`## Edge Semantics` explains how listed edges affect detection or interpretation.
`## Module Checks` lists what the node module checks or emits.

## Node Module

`nodes/<node-id>/module/main.py` is the only executable entrypoint for a node.
It should map the old unit fact-generator behavior into this node contract where
that old behavior exists. Shared code belongs in `nodes/module/`, not inside
multiple node modules.

The entrypoint should emit JSON compatible with `nodes/nodes/SCHEMA.md`.
