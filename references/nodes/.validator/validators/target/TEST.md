---
schema: validator-test.v1
validation_intent: target
---

# Node System Test

## Purpose

Prove that `references/nodes` is usable as the concept-unit replacement layer:
the layout is independent of `concepts`, node metadata lives in `NODE.md`, node
modules have a single entrypoint, and module output follows the node output
schema.

## Procedure

Run the validator module through the validator skill. Inspect any implemented
node directories under `nodes/` and compare their module entrypoint against
`nodes/SCHEMA.md`.

## Cases

| Case | Repo | Why this case exists | Pass signal |
|---|---|---|---|
| layout | n/a | ensures the new node system is not nested under concepts | validator audit and module checks pass |
| node-contract | n/a | ensures implemented nodes use `NODE.md` plus `module/main.py` | each implemented node has required docs and entrypoint |
| fact-compatibility | n/a | preserves the useful output shape from concept-unit fact generators | node module outputs match `nodes/SCHEMA.md` |

## Expectations

Deterministic checks should reject stale `semantics.md`, missing `NODE.md`,
missing module entrypoints, missing schema docs, and multiple schema versions.
Semantic scoring should focus on whether the node design improves reuse and
graph readiness without losing useful facts from the old concept-unit layer.

## Reporting

Report selected cases, validator module status, any stale concept coupling,
schema gaps, migration fidelity risks, and the highest-ROI next node migration.
