# Augur Pilot Execution Matrix

Use this reference for the first curated pilot set and bundle-comparison execution plan.

Pilot set source:
- [augur-pilot-repo-set-v1.json](./augur-pilot-repo-set-v1.json)

## Goal

Use the pilot matrix to compare:

- Augur vs generic
- backend model differences
- preload-policy differences
- regression over time

The first priority is not full coverage. It is a stable matrix that answers high-value product questions without exploding run count.

## Core Dimensions

### Repo dimension

Use a curated repo set with labels from:

- [augur-repo-label-schema.md](./augur-repo-label-schema.md)

### Analysis dimension

At minimum:

- `analysis_mode`
  - `full`
  - later `incremental`

### Backend dimension

At minimum:

- one strong primary model
- one secondary comparison model

### Agent mode dimension

- `augur`
- `generic`

### Preload-policy dimension

Current:

- `holistic`
- `selective`

Planned:

- `core`
- `guided`
- `targeted`
- `holistic`

When preload becomes stratified, split the dimension into:

- `framework_preload_policy`
- `concept_preload_policy`

### Repair policy dimension

At minimum record:

- `stop_at_valid`
- `quality_gate_enabled`

## Phase Order

### Phase 1. Baseline current-state quality

Run on a smaller pilot subset:

- `agent_mode=augur`
- strongest backend
- current default preload policy

Goal:

- confirm structural stability
- establish semantic score baseline

### Phase 2. Generic vs Augur

Same repos, same backend, same commit:

- `generic`
- `augur`

Goal:

- measure whether Augur materially improves semantic quality
- quantify runtime/token overhead

### Phase 3. Preload-policy comparison

Same repos, same backend, same commit, same agent mode:

- `augur + holistic`
- `augur + selective`

Later replace this with:

- `augur + core/guided`
- `augur + holistic`

Goal:

- determine whether broader preload materially improves quality
- determine where the quality gain is not worth the cost

### Phase 4. Quality-gate comparison

Same configuration except:

- `stop_at_valid`
- `quality_gate_enabled`

Goal:

- measure whether the extra repair loop improves semantic quality enough to justify runtime/tokens

### Phase 5. Over-time regression tracking

Repeat the chosen preferred configuration on the same repo set after substantial Augur changes.

Goal:

- prevent regressions
- attribute improvements to the correct layer

## Recommended Initial Matrix

For the first useful pilot:

```text
repos: 8-12
analysis_mode: full
backend_models: 1-2
agent_modes: augur + generic
preload_policies: 2
quality_gate: 1 initially, then compare 2
```

Keep the very first pass smaller if needed:

```text
8 repos * 1 backend * 2 agent modes * 2 preload policies = 32 runs
```

That is enough to answer the first preload question without turning benchmarking into a product of its own.

## Questions This Matrix Must Answer

1. Is Augur better than generic on the same repo and model?
2. Is the quality gain worth the runtime and token overhead?
3. Is `holistic` materially better than `selective`, or only on certain repo classes?
4. Which repo labels predict the need for broader preload?
5. Does quality gating improve semantic quality enough to justify extra repair loops?

## Output Requirements

Each matrix execution should produce:

- per-run manifest
- per-run scores
- snapshot comparison using:
  - [benchmark-comparison-schema.md](/kord/workstation/home/project/kordinate/shared/skills/audit/references/benchmark-comparison-schema.md)
- a short analyst summary covering:
  - best configuration overall
  - best configuration per repo bucket
  - major regressions
  - recommended next product change
