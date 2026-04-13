# Augur Layered Prompt Design

## Goal

Improve provider-side prompt caching and internal prompt discipline by separating Augur `/analyze` into stable layers.

The current runtime bundle is too monolithic:

- memory bundle content is inlined into the runtime bundle
- skill/runtime instructions and semantic preload are mixed together
- small changes can invalidate a much larger prompt prefix than necessary

## Design

Use four prompt layers.

### 1. Skill Core

Purpose:

- stable operational contract for `/analyze`
- mode handling
- execution order
- output expectations
- validation and report obligations

Recommended bundle:

```text
agents/augur/.generated/bundles/skill/analyze-core-v1.md
```

This should be the most cache-stable layer after agent identity.

### 2. Memory Preload

Purpose:

- semantic preload only
- selective vs holistic model-tier policy
- indexes, summaries, full semantics, targeted read rules

Recommended bundles:

```text
agents/augur/.generated/bundles/memory/analyze-selective-v1.md
agents/augur/.generated/bundles/memory/analyze-holistic-v1.md
```

This layer should change independently from the skill contract.

### 3. Detector / Execution Plan References

Purpose:

- deterministic pipeline entrypoints
- detector execution plan references
- detector bundle locations
- optional narrow reminders about the evidence flow

This should stay compact. It should not inline large detector bundles into the prompt.

### 4. Repo / Run Context

Purpose:

- project path
- current mode
- changed files or affected components
- facts/concepts already produced
- task-specific instructions

This is the least cacheable layer and should be appended last.

## Recommended Composition Order

1. agent identity / system prefix
2. skill core
3. memory preload
4. detector execution references
5. repo/run context

That ordering maximizes reuse of the stable prefix.

## Bundle Policy

### Large-context models

Use:

- `skill core`
- `holistic memory`
- repo/run context

The point is to keep broad semantics resident before the repo-specific material arrives.

### Constrained models

Use:

- `skill core`
- `selective memory`
- repo/run context

The point is to preserve room for repo evidence while still giving the model the ontology and read rules.

## What Should Change Less Often

Most stable:

- skill core
- selective/holistic memory family names

Moderately stable:

- memory bundle contents
- detector execution plan references

Most volatile:

- repo/run context
- changed-file slices
- benchmark prompts

## Practical Implication

The current `.generated/bundles/runtime/analyze-*.json` files should stop inlining full memory bundle text.

Instead, runtime composition should be treated as:

- a manifest or plan
- not a giant concatenated prompt artifact

Suggested runtime manifest shape:

```json
{
  "skill_bundle": ".generated/bundles/skill/analyze-core-v1.md",
  "memory_bundle": ".generated/bundles/memory/analyze-selective-v1.md",
  "detector_plan": ".generated/bundles/detectors/execution-plan.json",
  "composition_order": [
    "skill_bundle",
    "memory_bundle",
    "detector_plan",
    "repo_context"
  ]
}
```

## Immediate Refactor

1. introduce a dedicated skill bundle
2. keep memory bundle generation as-is for now
3. replace giant runtime markdown bundles with compact runtime manifests
4. let the caller or runner compose the final prompt in a fixed order

## Expected Benefit

- better prompt cache locality
- clearer ownership of changes
- easier bundle evaluation
- less accidental duplication across skill and memory layers
