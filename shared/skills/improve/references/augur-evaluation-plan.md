# Augur Analyze Evaluation Plan

Evaluation plan for running `agents/augur/skills/analyze` on the benchmark repo set and scoring the results consistently.

## Goal

Measure whether Augur `/analyze` produces:

- grounded architecture understanding
- useful component and flow decomposition
- accurate concept detection
- plausible failure-mode coverage
- schema-valid output
- better results than comparison models on the same repos

## Evaluation Unit

The basic unit is one:

`(model_or_agent, repo, pinned_sha, memory_bundle, skill_bundle, run_number)`

tuple.

Each evaluation unit should store:

- prompt used
- repo URL
- pinned SHA
- model or agent name
- memory bundle
- skill bundle
- run number
- wall-clock duration
- token usage if available
- stage timings
- output paths
- validation results
- scoring results

## What Gets Evaluated

### Hard gates

Every run should first pass:

- output files exist
- atlas parses
- atlas schema validates
- `grounded_in` file references resolve
- `metadata.analyzed_at_sha` matches the repo commit under test

Failing a hard gate should cap the repo score and mark the run as operationally failed even if some content is still useful.

### Scored dimensions

For each successful run, score:

- `concepts`
  - precision / recall / F1 against labeled concepts and anti-patterns
- `components`
  - top-level component quality and boundary accuracy
- `api_surface`
  - route family and major endpoint accuracy
- `externals_and_state`
  - important services, clients, stores, and ownership
- `failure_modes`
  - whether key external/state failures are identified
- `grounding`
  - whether checked claims are supported by cited files
- `stories`
  - whether critical components and flows are covered without ungrounded claims
- `incremental_mode`
  - full / incremental / skip correctness when evaluated on changed snapshots

## Bundle-Aware Evaluation

Augur should not be evaluated as one monolithic configuration.

The benchmark should explicitly test bundle combinations:

- `selective + selective`
- `selective + holistic`
- `holistic + selective`
- `holistic + holistic`

This allows the benchmark to separate:

- model effects
- memory-bundle effects
- skill-bundle effects
- interaction effects between memory and skill breadth

## Performance Logging

Performance should be logged per run and per stage.

### Required whole-run metrics

- `runtime_ms_total`
- `tokens_in`
- `tokens_out`
- `tokens_total`
- `estimated_cost`
- `success`
- `failure_reason` when applicable

### Required stage timings

Store:

- `runtime_ms.setup`
- `runtime_ms.gather`
- `runtime_ms.facts`
- `runtime_ms.concepts`
- `runtime_ms.atlas`
- `runtime_ms.stories`
- `runtime_ms.validation`
- `runtime_ms.total`

Stage definitions:

- `setup`
  - repo resolution, previous atlas lookup, mode decision
- `gather`
  - source discovery, file scoping, stack detection
- `facts`
  - deterministic extraction and normalization
- `concepts`
  - concept inference and semantic detection
- `atlas`
  - synthesis of components, dependencies, API, state, failure modes, debt
- `stories`
  - composition and refinement
- `validation`
  - schema and validator work

## Performance-Aware Scoring

Quality and efficiency should be reported separately and together.

For each run, report:

- `quality_score`
- `runtime_ms_total`
- `tokens_total`
- `estimated_cost`
- `quality_per_minute`
- `quality_per_1k_tokens`

For each configuration family, report:

- mean quality
- mean runtime
- mean tokens
- quality variance
- stage-time breakdown

This prevents a slower bundle from looking better without exposing the operational cost.

## Label Strategy

Do not fully gold-label every atlas section.

For each repo, maintain a compact label file with:

- `critical_components`
- `expected_concepts`
- `expected_anti_patterns`
- `expected_route_families`
- `expected_external_dependencies`
- `expected_state_stores`
- `expected_failure_modes`
- `grounding_check_queries`
- `notes_on_ambiguity`

Ambiguous items should be flagged and excluded from hard numeric scoring.

## Grounding Checks

Grounding should be audited directly against source files, not against the model's own summary.

Recommended procedure:

1. Sample `10-20` claims per repo from:
   - components
   - dependencies
   - API surface
   - failure modes
   - stories
2. For each claim:
   - read the cited file(s)
   - mark `supported`, `weakly_supported`, or `unsupported`
3. Compute:
   - strict grounding rate = `supported / total`
   - relaxed grounding rate = `(supported + weakly_supported) / total`

Strict grounding rate should be the reported metric.

## Scoring Weights

Recommended overall weighting:

- `25%` concepts
- `20%` components
- `15%` grounding
- `10%` API surface
- `10%` externals + state
- `10%` failure modes
- `5%` incremental correctness
- `5%` stories

If schema validation fails, cap the total repo score at `0.40`.
If strict grounding is below `0.50`, cap the story score at `0`.

## Comparative Evaluation

When comparing Augur with Gemini, Claude, DeepSeek, or other baselines:

- use the same repo and commit
- use the same prompt structure
- require the same output shape
- align timeouts and retry policy
- align the number of runs for variance estimation
- compare the same bundle settings where applicable

Comparison metrics:

- absolute repo score
- head-to-head winner by repo
- win rate by bucket
- win rate by language
- win rate by size class
- quality per second
- quality per token
- bundle interaction effects

## Run Schedule

Use two suites.

### Core suite

Run on every meaningful change:

- `20` repos
- full `2x2` bundle matrix
- `1` run each for routine checks
- `3` repeated runs on a small separation subset when prompt, bundles, or scoring changes materially

### Extended suite

Run nightly or before releases:

- full curated set
- top `1-2` bundle configurations per model
- repeated runs on separation and adversarial repos

## Incremental Evaluation

Augur has explicit `full`, `incremental`, and `skip` modes, so benchmarking should include changed snapshots.

Recommended method:

1. Pin a base commit for a repo.
2. Pick one later commit with:
   - small scoped change
   - medium cross-component change
   - docs-only or peripheral change
3. Score whether Augur selected:
   - `skip` when appropriate
   - `incremental` when topology is mostly stable
   - `full` when topology changed enough to justify it

This should be measured separately from content quality.

## Human Review Workflow

Use a lightweight reviewer worksheet per repo:

- Was the top-level architecture basically right?
- Were the most important components present?
- Were the detected concepts mostly right?
- Did the stories say anything impressive but false?
- Did the model miss an obvious dependency or failure mode?
- Would this output actually help a human onboard to the repo?

This reviewer pass should not replace numeric scoring. It should explain surprising scores and resolve edge cases.

## Suggested File Layout

Recommended benchmark layout:

```text
benchmark/
  candidates/
  curated/
  labels/
  runs/
  scorecards/
  reports/
  manifests/
```

Per-repo label file:

```text
benchmark/labels/<owner>--<repo>.json
```

Per-run output:

```text
benchmark/runs/<timestamp>/<model>/<memory-bundle>__<skill-bundle>/<owner>--<repo>/
```

Per-run manifest:

```text
benchmark/manifests/<timestamp>/<model>/<memory-bundle>__<skill-bundle>/<owner>--<repo>.json
```

## Suggested Run Manifest

Each run manifest should look roughly like:

```json
{
  "repo": "owner/name",
  "pinned_sha": "abc123",
  "model": "augur",
  "memory_bundle": "selective",
  "skill_bundle": "holistic",
  "run_number": 1,
  "analysis_mode": "full",
  "success": true,
  "runtime_ms": {
    "setup": 1200,
    "gather": 8400,
    "facts": 5300,
    "concepts": 9400,
    "atlas": 4100,
    "stories": 7300,
    "validation": 1400,
    "total": 37100
  },
  "tokens": {
    "input": 42000,
    "output": 6300,
    "total": 48300
  },
  "estimated_cost": 0.00,
  "outputs": {
    "atlas": "...",
    "stories_dir": "...",
    "facts_dir": "..."
  },
  "validation": {
    "schema_valid": true,
    "grounding_refs_resolve": true
  },
  "scores": {
    "quality_score": 0.81,
    "concepts_f1": 0.79,
    "grounding": 0.86
  }
}
```

## Minimum Viable Evaluation

To start quickly:

1. curate `12-20` repos
2. create compact label files
3. run Augur on the core `2x2` bundle matrix for a small subset
4. run one comparison model on the same subset
5. validate schema and grounding
6. score concepts, components, externals, failure modes, and stories
7. inspect stage timings and bundle tradeoffs
8. manually review the surprising cases

This is enough to get a credible first benchmark before scaling to the full dataset.
