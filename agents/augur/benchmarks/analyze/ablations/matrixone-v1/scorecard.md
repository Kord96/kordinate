# MatrixOne Ablation Scorecard

Use one row per condition.

| condition | validator_status | errors | warnings | warning_kinds | repair_iterations | structural_score | architecture_score | grounding_score | teaching_score | provenance_score | semantic_score | runtime_ms | tokens_total | estimated_cost | failure_attribution | notes |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| bare-model | `valid` | 0 | 0 | `{}` | 2 | 1.00 | 0.76 | 0.78 | 0.72 | 1.00 | 0.79 |  |  |  | `teaching-structure-gap` | Stronger than expected. Plausible backbone with `service-bootstrap`, `compute-node`, `transaction-node`, `log-service`, `access-proxy`, but naming is generic and file-service remains subordinate instead of becoming a cross-cutting root. |
| skill-no-facts | `valid` | 0 | 0 | `{}` | 4 | 1.00 | 0.88 | 0.86 | 0.89 | 1.00 | 0.89 |  |  |  | `none-dominant / mild grounding-risk` | Best surprise. Workflow + schemas + repair loop alone produced a near-Augur result: `cluster-runtime`, `query-compute`, `transaction-storage`, `log-coordination`, with strong child stories and narratives. |
| facts-no-memory | `invalid` | 73 | 3 | `{\"story-quality\": 73, \"narrative-selection\": 2, \"grounding\": 1}` | 2 | 0.05 | 0.72* | 0.40* | 0.30* | 0.85 | N/A |  |  |  | `component-synthesis-gap` | After correcting repo-root validation, the provenance blow-up disappeared, but the condition still failed badly: stories referenced component ids like `cn-query-runtime`, `tn-shard-runtime`, and `file-object-storage` that did not exist in the atlas. This suggests deterministic facts alone can inspire plausible roots, but without Augur workflow discipline they are not enough to keep atlas/story contracts coherent. |
| current-policy | `valid` | 0 | 0 | `{}` | 4 | 1.00 | 0.92 | 0.90 | 0.91 | 1.00 | 0.92 |  |  |  | `none-dominant` | Best overall. More repo-shaped roots (`service-runtime`, `cn-query-runtime`, `transaction-storage`, `log-ha-coordination`, `file-service`), stronger child-story structure, and cleaner cross-cutting subsystem promotion than the baselines. |

## Required notes

- keep the backend model constant
- keep the repo and commit constant
- do not reuse semantic outputs across conditions
- record whether the result was merely structurally valid or actually quality-clean
- scores above are provisional first-pass human scores, not final benchmark canon
- `facts-no-memory` was rerun with `AUGUR_PROJECT_ROOT` set. The remaining failure is now structural semantic inconsistency rather than path resolution.
