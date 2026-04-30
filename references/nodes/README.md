---
schema: node-system.v1
---

# Nodes

Nodes replace concept units as the ontology layer. A node owns one reusable
detection contract and may use deterministic code, semantic guidance, or both.

Layout:

```text
nodes/
  README.md
  SCHEMA.md
  module/          # reusable helpers imported by individual node modules
  nodes/
    SCHEMA.md      # node output schema
    <node-id>/
      NODE.md      # frontmatter plus semantic contract
      module/
        main.py    # single executable entrypoint for the node
```

`nodes/module/` is for shared runtime code only. Individual node modules should
import it instead of copying common parsing, evidence, normalization, or payload
helpers.
