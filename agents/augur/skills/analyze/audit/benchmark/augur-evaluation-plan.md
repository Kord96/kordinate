# Augur Evaluation Plan

Use this reference for scoring Augur outputs consistently across repos, models, and bundle configurations.

## Goal

Provide one benchmark language for deciding:

- whether Augur quality is improving or regressing
- whether a preload policy is worth its cost
- whether a detector or prompt change improved the right layer
- whether a configuration is good enough for pilot or product use

This plan is for current-state `/analyze`, not historical timeline synthesis.

## Score Layers

Benchmark every run at three layers:

1. Structural quality
2. Semantic quality
3. Efficiency

Keep these separate. A run can be structurally valid and still semantically mediocre.

## Structural Quality

Use validator and repair-loop outputs as the structural layer.

Record at minimum:

- `validator_status`
- `error_count`
- `warning_count`
- `warning_count_by_kind`
- `open_semantic_conflict_count`
- `repair_iteration_count`
- `final_medium_priority_count`
- `final_high_priority_count`

Suggested normalized score:

```text
structural_score = 1.0
- 1.0 if error_count > 0
- 0.20 * min(1, open_semantic_conflict_count / 3)
- 0.10 * min(1, final_high_priority_count / 2)
- 0.08 * min(1, final_medium_priority_count / 4)
- 0.05 * min(1, repair_iteration_count / 5)
```

Clamp to `[0, 1]`.

Practical interpretation:

- `0.90-1.00` excellent structural health
- `0.75-0.89` acceptable but noisy
- `<0.75` not benchmark-clean

## Semantic Quality

Semantic quality should be human-scored at first on a 1-5 rubric, then normalized to `[0,1]`.

### Dimensions

- `architecture_score`
  - are top-level components correct and repo-shaped?
  - are dependency directions correct?
  - is state modeled truthfully?
- `grounding_score`
  - do claims sound like the code they cite?
  - are grouped grounding targets small and reasonable?
- `teaching_score`
  - do stories decompose naturally?
  - do narratives use the most useful child stories?
- `provenance_score`
  - do cited files and modules exist?
  - is the output navigable and trustworthy?

### Suggested rubric

Use 1-5 per dimension:

- `1` broken or misleading
- `2` materially weak
- `3` usable but clearly incomplete
- `4` strong
- `5` excellent

Normalize as:

```text
normalized = (raw_score - 1) / 4
```

### Composite semantic score

Suggested weighting:

- `architecture_score`: `0.40`
- `grounding_score`: `0.25`
- `teaching_score`: `0.25`
- `provenance_score`: `0.10`

This yields:

```text
semantic_score =
  0.40 * architecture_score +
  0.25 * grounding_score +
  0.25 * teaching_score +
  0.10 * provenance_score
```

## Efficiency

Use the dimensions already defined in:

- [benchmark-comparison-schema.md](/kord/workstation/home/project/kordinate/shared/skills/audit/references/benchmark-comparison-schema.md)

Track at minimum:

- `runtime_ms`
- `tokens_in`
- `tokens_out`
- `tokens_total`
- `estimated_cost`
- `cache_hit_ratio`
- `uncached_prefix_bytes`

Derived metrics:

- `quality_per_second`
- `quality_per_1k_tokens`
- `quality_per_dollar`

## Overall Score

For product-quality comparisons, use:

```text
overall_score =
  0.30 * structural_score +
  0.55 * semantic_score +
  0.15 * efficiency_score
```

`efficiency_score` should be a normalized comparison score inside the experiment cohort, not a global absolute score.

If you do not have a stable efficiency normalization yet, compare:

- `structural_score`
- `semantic_score`

first, and use raw runtime/tokens as the efficiency view.

## Acceptance Thresholds

### Benchmark-clean

- `error_count == 0`
- `open_semantic_conflict_count == 0`
- `final_high_priority_count == 0`
- `semantic_score >= 0.70`

### Pilot-quality

- benchmark-clean
- `final_medium_priority_count == 0`
- `grounding_score >= 0.75`
- `teaching_score >= 0.75`
- `overall_score >= 0.78`

### Excellent

- pilot-quality
- `warning_count` is low and mostly low-priority grounding residue
- `semantic_score >= 0.85`
- `grounding_score >= 0.85`
- `teaching_score >= 0.85`

## Failure Attribution

Every benchmark review should classify the dominant failure layer:

- `deterministic-extraction-gap`
- `component-synthesis-gap`
- `story-decomposition-gap`
- `grounding-gap`
- `repair-loop-gap`
- `bundle-policy-gap`
- `runtime-platform-gap`

This is required. Otherwise benchmark failures do not turn into concrete product work.

## Bundle / Preload Evaluation

Do not treat the benchmark only as `holistic vs selective`.

The benchmark system should support preload-policy experiments across semantic strata such as:

- `core`
- `guided`
- `targeted`
- `holistic`

and should treat framework preload and concept preload as separate dimensions when the system supports that split.

Questions the evaluation plan must answer:

- what should always be loaded?
- what should be loaded from deterministic signals?
- what should be loaded only on demand?
- when does `holistic` materially justify its cost?

## Run Record

Each run should record:

- repo id and commit
- analysis mode
- preload policy / bundle policy
- backend model
- structural metrics
- semantic rubric scores
- efficiency metrics
- dominant failure attribution
- short human summary

## Minimum Deliverables

Every benchmark snapshot should include:

- raw run manifests
- comparison snapshot
- repo labels
- semantic scoring sheet or equivalent human review artifact
- a short conclusions file with:
  - what improved
  - what regressed
  - what to change next
