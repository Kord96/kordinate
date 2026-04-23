# MatrixOne Ablation Scorecard v2

| condition | validator_status | errors | warnings | structural_score | architecture_score | grounding_score | teaching_score | provenance_score | semantic_score | runtime_ms | failure_attribution | notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| raw-model |  |  |  |  |  |  |  |  |  |  |  |  |
| schemas-only |  |  |  |  |  |  |  |  |  |  |  |  |
| schemas-plus-validator |  |  |  |  |  |  |  |  |  |  |  |  |
| facts-plus-validator |  |  |  |  |  |  |  |  |  |  |  |  |
| current-policy |  |  |  |  |  |  |  |  |  |  |  |  |

## Notes

- `raw-model` and `schemas-only` may not produce validator-clean outputs
- compare them qualitatively first, structurally second
- this matrix is intended to isolate the contribution of schemas, validator/repair, and deterministic facts more cleanly than `matrixone-v1`
