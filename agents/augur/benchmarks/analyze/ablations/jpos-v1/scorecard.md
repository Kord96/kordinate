# jPOS Ablation Scorecard

Use one row per condition.

| condition | validator_status | errors | warnings | warning_kinds | repair_iterations | structural_score | architecture_score | grounding_score | teaching_score | provenance_score | semantic_score | runtime_ms | tokens_total | estimated_cost | failure_attribution | notes |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| bare-model |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| skill-no-facts |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| facts-no-memory |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| current-policy |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

## Required notes

- keep the backend model constant
- keep the repo and commit constant
- do not reuse semantic outputs across conditions
- record whether the result was merely structurally valid or actually quality-clean
- compare results against MatrixOne and RustPBX before concluding what generalizes
