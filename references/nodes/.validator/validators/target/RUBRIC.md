---
schema: validator-rubric.v1
validation_intent: target
---

# Node System Rubric

## Rubric

| Signal | Weight | Source | Success Condition | Error Condition | Scoring Guidance |
|---|---:|---|---|---|---|
| Replacement Boundary | 0.15 | `README.md`, `SCHEMA.md`, and old concept-unit behavior. | Nodes are clearly positioned as the replacement for concepts, not a nested concept subtype. | The layout or docs still treat nodes as a child of concepts or duplicate the concept-unit contract without simplification. | Score clarity of ownership, migration boundary, and stale concept coupling. |
| Node Contract | 0.25 | `SCHEMA.md`, `nodes/SCHEMA.md`, `nodes/<node>/NODE.md`, and validator module output. | Every node has one `NODE.md`, one module entrypoint, one schema version, and one documented output contract. | Nodes split metadata across files, use multiple schema versions, or omit required node/module files. | Score schema completeness, section clarity, and deterministic enforceability. |
| Reusable Module Design | 0.15 | `module/`, node modules, and copied helper logic. | Shared helper code belongs in `nodes/module/`; node modules stay thin and import common behavior. | Common parsing, evidence formatting, or fact payload logic is duplicated across node modules. | Score reuse, importability, and resistance to per-node drift. |
| Unit Migration Fidelity | 0.20 | Existing concept unit fact-generators, migration notes, and node module behavior. | Old fact-generator behavior can be mapped into node module entrypoints without losing useful facts. | Migration loses frontmatter meaning, drops useful facts, or overfits nodes to a single repository. | Score preservation of signal, frontmatter fidelity, and generalization. |
| Graph Readiness | 0.15 | `NODE.md` edges and abstraction levels. | Nodes express relationships and abstraction levels well enough to support a future ontology graph. | Edges are missing, arbitrary, or encode confidence/policy outside the graph relationship model. | Score edge semantics, abstraction calibration, and graph composability. |
| Dataset Coverage | 0.10 | Tests, fixtures, benchmark repos, and expected outputs. | Validation covers enough representative cases to trust node behavior beyond examples. | Coverage is missing, planned-only, or benchmark-specific enough to hide overfitting. | Score quantity, diversity, oracle quality, and transfer beyond known repos. |
