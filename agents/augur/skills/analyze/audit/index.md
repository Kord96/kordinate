---
description: Canonical audit entrypoint for Augur /analyze.
---

# Augur Analyze Audit

Use this file with the shared `/audit` skill. Keep the audit tight: choose the narrowest mode that answers the question.

## Modes

### Structural

Use when checking:
- contract drift
- stale paths
- schema mismatches
- missing generated artifacts
- detector and fact plumbing

Primary files:
- [SKILL.md](../SKILL.md)
- [atlas-schema.md](/kord/workstation/home/project/kordinate/agents/augur/schemas/atlas-schema.md)
- [story-schema.md](/kord/workstation/home/project/kordinate/agents/augur/schemas/story-schema.md)
- [narratives-schema.md](/kord/workstation/home/project/kordinate/agents/augur/schemas/narratives-schema.md)
- [meta-schema.md](/kord/workstation/home/project/kordinate/agents/augur/schemas/meta-schema.md)
- [augur-output-contract.md](/kord/workstation/home/project/kordinate/agents/augur/schemas/augur-output-contract.md)
- [snapshot-layout.md](./runtime/snapshot-layout.md)
- [blast-radius-schema.md](./runtime/blast-radius-schema.md)
- [facts-schema.md](/kord/workstation/home/project/kordinate/agents/augur/schemas/facts-schema.md)
- [build_detector_bundles.py](/kord/workstation/home/project/kordinate/agents/augur/scripts/build/build_detector_bundles.py)
- [synthesize_atlas_from_facts.py](/kord/workstation/home/project/kordinate/agents/augur/scripts/synthesize_atlas_from_facts.py)
- [fact_extractor_support.py](/kord/workstation/home/project/kordinate/agents/augur/scripts/fact_extractor_support.py)

### Semantic

Use when checking:
- concept quality
- detector-to-meaning mismatch
- question quality
- memory quality
- reflection usefulness

Primary files:
- [component-model.md](../references/component-model.md)
- [detection-method.md](../references/detection-method.md)
- [dependency-map.md](../references/dependency-map.md)
- [api-surface.md](../references/api-surface.md)
- [tension-signals.md](../references/tension-signals.md)
- [semantic-review-prompt.md](./prompts/semantic-review.md)
- [reflection-prompt.md](./prompts/reflection.md)
- [concept-decision-design.md](/kord/workstation/home/project/kordinate/agents/augur/scripts/notes/concept-decision-design.md)
- [README.md](/kord/workstation/home/project/kordinate/agents/augur/detectors/facts/concept-evidence/README.md)
- [schema.md](/kord/workstation/home/project/kordinate/agents/augur/detectors/facts/concept-evidence/schema.md)
- [meta-schema.md](/kord/workstation/home/project/kordinate/agents/augur/memory/catalog/concepts/meta-schema.md)

### Runtime

Use when checking:
- live execution verification
- output artifact verification
- telemetry verification
- caching verification
- reflection capture verification

Primary files:
- [augur-e2e-checklist.md](./runtime/augur-e2e-checklist.md)
- [augur-run-manifest-schema.md](./runtime/augur-run-manifest-schema.md)
- [augur-reflection-integration.md](./runtime/augur-reflection-integration.md)
- [augur-reflection-record-schema.md](./runtime/augur-reflection-record-schema.md)
- [blast-radius-schema.md](./runtime/blast-radius-schema.md)
- [snapshot-layout.md](./runtime/snapshot-layout.md)

### Benchmark

Use when checking:
- model comparison
- generic vs augur comparison
- bundle comparison
- over-time comparison

Primary files:
- [augur-benchmark-dataset.md](./benchmark/augur-benchmark-dataset.md)
- [augur-evaluation-plan.md](./benchmark/augur-evaluation-plan.md)
- [augur-pilot-execution-matrix.md](./benchmark/augur-pilot-execution-matrix.md)
- [augur-pilot-repo-set-v1.json](./benchmark/augur-pilot-repo-set-v1.json)
- [augur-repo-label-schema.md](./benchmark/augur-repo-label-schema.md)
- [benchmark-comparison-schema.md](/kord/workstation/home/project/kordinate/shared/skills/audit/references/benchmark-comparison-schema.md)
- [reflection-analysis-schema.md](/kord/workstation/home/project/kordinate/shared/skills/audit/references/reflection-analysis-schema.md)
- [codesight-fact-layer-gap-analysis.md](/kord/workstation/home/project/kordinate/agents/augur/scripts/notes/codesight-fact-layer-gap-analysis.md)

### Loop

Use when the audit should drive edits.

Order:
1. run structural
2. run semantic
3. run runtime or benchmark as needed
4. apply the smallest useful fix in the correct layer
5. rerun and report deltas
