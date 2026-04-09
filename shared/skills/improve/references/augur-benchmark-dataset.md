# Augur Analyze Benchmark Dataset

Design for a cross-model benchmark dataset for `agents/augur/skills/analyze`.

This benchmark is meant to evaluate:

- absolute quality of Augur `/analyze`
- relative quality versus other models or agents
- regression resistance over time
- grounding, precision, and schema compliance under realistic repository conditions

## Goals

The dataset should answer these questions:

- Does `/analyze` correctly identify architecture, concepts, dependencies, API surface, state, and failure modes?
- Does it stay grounded in the code rather than inferring architecture from naming alone?
- Does it preserve output quality across languages, repo sizes, and topology styles?
- Does it outperform or match competing models on realistic architectural analysis tasks?
- Which repos actually separate stronger architectural analysis from shallow pattern matching?

## Portfolio Shape

Use a fixed `72`-repo benchmark portfolio.

### Buckets

- `12 anchors`
  - Stable, well-understood repos with documented architecture or known concepts.
  - Used for regression detection.
- `36 production`
  - Real repositories that resemble likely user inputs.
  - Used for overall usefulness and coverage.
- `12 adversarial`
  - Repos chosen to trigger false positives, weak grounding, or overconfident summaries.
  - Used for precision and robustness.
- `12 separation`
  - Repos selected because different models are likely to diverge materially on them.
  - Used for head-to-head comparison.

### Language Mix

Target mix for the 72 repos:

- `18 Python`
- `18 TypeScript`
- `14 Go`
- `14 Java`
- `8 mixed / monorepo / oddball`

### Size Mix

Target distribution:

- `18 small` — under roughly `5k` LOC
- `30 medium` — roughly `5k-40k` LOC
- `18 large` — roughly `40k-200k` LOC
- `6 very large / monorepo-ish`

### Topology Mix

Ensure repeated representation of:

- library / framework
- API service
- worker / job system
- CLI / tooling repo
- monolith
- multi-package repo
- event-driven system
- config-heavy or infra-heavy repo

No topology that matters should appear in fewer than `5` repos across the set.

## Why This Shape

Random popular repos are not enough. The benchmark should include:

- easy canonical cases for regression testing
- messy real-world repos for practical value
- adversarial cases to test precision and grounding
- discriminative cases that produce stable differences between models

For cross-model testing, discriminative coverage matters more than raw variety. A repo that every model gets right is useful as an anchor, but not very useful for ranking. A repo where careful models consistently outperform shallow ones is far more valuable.

## What To Label

Do not attempt to fully gold-label the entire atlas on day one. Start with the highest-value benchmark fields.

### Required labels

- `analysis_mode`
  - full / incremental / skip
- `critical_components`
  - top-level components and major boundaries
- `expected_concepts`
  - detected patterns
- `expected_anti_patterns`
  - anti-patterns and gaps when evidence is strong
- `expected_api_surface`
  - route families, handlers, approximate endpoint count
- `expected_external_dependencies`
  - important external clients or services
- `expected_state_stores`
  - primary stores and state ownership
- `expected_failure_modes`
  - high-value failures for external and stateful components
- `grounding_checks`
  - claims verified against cited files
- `schema_validity`
  - whether output satisfies the expected contract
- `story_coverage`
  - whether critical components and flows are covered

### Labeling philosophy

- Label what is necessary to compare outputs reliably.
- Prefer partial high-confidence labels over exhaustive low-confidence labels.
- Exclude ambiguous cases from hard metrics and keep them as review notes.

## Scoring

Use three layers of scoring.

### 1. Hard gates

These are pass/fail checks:

- output files exist
- output parses
- schema contract is valid
- cited grounding paths exist
- references point to the correct repo snapshot

If a hard gate fails, cap the repo score.

### 2. Task scores

Score the quality of the analysis itself:

- `concepts` — precision / recall / F1
- `components` — boundary and topology accuracy
- `grounding` — fraction of tested claims supported by cited files
- `api_surface` — route family and endpoint accuracy
- `externals_and_state` — major services and stores found
- `failure_modes` — meaningful failure coverage
- `incremental_mode` — correct full / incremental / skip decision
- `stories` — grounding and useful coverage

Suggested weighting:

- `25%` concepts
- `20%` components / topology
- `15%` grounding
- `10%` API surface
- `10%` externals + state
- `10%` failure modes
- `5%` incremental correctness
- `5%` stories

### 3. Comparative scores

These are for model-vs-model analysis:

- head-to-head win rate by repo
- win rate by bucket
- win rate by language
- win rate by size class
- cost-normalized quality
- latency-normalized quality
- run-to-run variance

## Repeated Runs

Cross-model evaluation needs variance estimates.

Recommended repeated-run plan:

- `12 separation repos x 3 runs`
- `8 adversarial repos x 2 runs`
- all remaining repos `x1`

This helps distinguish model quality from sampling luck or response instability.

## Core vs Extended Suites

Maintain two suites.

### Core suite

`20` repos:

- `6 anchors`
- `8 production`
- `3 adversarial`
- `3 separation`

Use this suite on every important skill or detector change.

### Extended suite

Full `72` repos.

Use this suite for nightly comparisons, release checks, or major benchmark reviews.

## Candidate Selection Rules

A repo should enter the candidate pool only if it tests something specific.

### Good candidate properties

- architecture is present and inferable
- enough complexity to require real analysis
- signals are spread across code, config, models, routes, or infra
- likely to expose strengths or weaknesses in grounding or precision
- not too trivial
- not too large to evaluate realistically

### Candidate rejection rules

Reject repos that are:

- mostly generated or vendored code
- too small to express meaningful architecture
- too large to benchmark cheaply and consistently
- duplicates of already-covered frameworks or topologies without adding new value
- impossible to label with reasonable confidence

## Cross-Model Fairness Rules

When comparing Augur against Gemini, Claude, DeepSeek, GLM-5, or others:

- use the same pinned commit SHA
- use the same repo snapshot and file tree
- use the same benchmark prompt structure
- require the same output schema
- keep retry policy and timeout policy aligned
- keep token budget classes comparable where possible
- avoid model-specific hints in the benchmark prompt
- record the `memory_bundle` and `skill_bundle` used for each run

Otherwise, the benchmark measures prompt adaptation rather than analysis quality.

## Bundle Matrix

Augur configuration should be benchmarked as a first-class variable.

Each run should record:

- `memory_bundle`
- `skill_bundle`

Recommended core matrix:

- `selective + selective`
- `selective + holistic`
- `holistic + selective`
- `holistic + holistic`

This is the minimum useful matrix for understanding:

- whether memory breadth helps
- whether skill breadth helps
- whether they interact
- whether gains are worth the additional runtime and token cost

### Execution strategy

Use the full `2x2` matrix on the core suite.

For the extended suite, keep only:

- the top `1-2` configurations per model from the core-suite results

This keeps the factorial experiment tractable while still preserving meaningful bundle comparisons.

## Performance Instrumentation

Performance should be measured at both whole-run and stage levels.

### Whole-run metrics

- wall-clock duration
- input tokens
- output tokens
- total tokens
- estimated cost
- timeout / failure rate

### Stage-level timing

Every run should capture timing for:

- `setup`
  - repo resolution, atlas lookup, mode determination
- `gather`
  - file discovery, changed-file mapping, stack detection
- `facts`
  - extraction and normalization
- `concepts`
  - inference and concept detection
- `atlas`
  - synthesis of components, dependencies, API, state, failures, debt
- `stories`
  - narrative composition
- `validation`
  - schema or validator passes
- `total`

This breakdown is enough to identify bottlenecks without over-instrumenting the pipeline.

## Performance-Aware Comparison

Do not compare configurations on quality alone.

Report:

- `quality score`
- `runtime`
- `tokens`
- `cost`
- `quality per minute`
- `quality per 1k tokens`
- `stage time distribution`

This makes it possible to answer:

- whether `holistic` actually improves outcomes
- whether it only helps on certain repo classes
- whether it improves useful dimensions or only expensive ones
- which stage is paying for the gain

## Candidate Database

Maintain a candidate database before final curation. The database should contain more repos than the final benchmark so weak or duplicate candidates can be filtered out.

### Recommended size

Collect `150-250` candidates before reducing to the final `72`.

This gives enough room to remove:

- duplicates
- boring repos
- unlabeled or unlabelable repos
- repos that every model solves equally
- repos that are too unstable or too expensive

### Candidate fields

Each candidate should store:

- `repo`
- `url`
- `pinned_sha`
- `suggested_by`
- `language`
- `secondary_languages`
- `bucket_candidates`
- `size_bucket`
- `topology_tags`
- `framework_tags`
- `reason_for_inclusion`
- `expected_signals`
- `expected_failure_modes`
- `difficulty`
- `noise_risks`
- `licensing_notes`
- `selection_status`
- `selection_notes`

## Model-Sourced Suggestions

Use multiple models to suggest candidate repos, but do not let them directly define the final benchmark.

Each model should be treated as a candidate generator, not a curator.

### Why involve multiple models

Different models surface different repo sets:

- some favor canonical framework repos
- some find more niche or adversarial repos
- some are better at suggesting messy real-world examples

This is useful at candidate-generation time. It is not sufficient for final selection because models will often suggest:

- redundant repos
- repos they personally recognize best
- repos that are popular rather than discriminative

## Repo Suggestion Protocol

Ask each model to propose candidates in the same structured format.

### Instructions for every model

Request:

- exactly `N` repo suggestions
- no duplicates within its own list
- only public repos
- each suggestion must name a proposed bucket
- each suggestion must explain what benchmark property it tests
- each suggestion must include expected concepts or repo signals
- each suggestion must include at least one risk or caveat

### Suggested request dimensions

Ask each model for:

- `10 anchors`
- `20 production`
- `10 adversarial`
- `10 separation`

That yields `50` suggestions per model. With `4-5` models, this should produce a strong candidate pool after de-duplication.

### Output format

Prefer JSON lines or JSON array with this shape:

```json
{
  "repo": "owner/name",
  "bucket": "anchor",
  "language": "python",
  "topology_tags": ["api", "framework"],
  "framework_tags": ["fastapi"],
  "reason_for_inclusion": "Canonical FastAPI architecture with strong router and DI signals.",
  "expected_signals": ["dependency-injection", "router", "middleware"],
  "expected_failure_modes": ["hallucinated component boundaries", "overgeneralized DI usage"],
  "difficulty": "medium",
  "noise_risks": ["large docs tree"],
  "selection_notes": "Good anchor candidate for Python web stack."
}
```

### Prompt design guidance

The prompt to each external model should explicitly say:

- suggest repos for a benchmark, not for personal use
- optimize for diversity and discriminative value
- avoid only suggesting the most famous repos
- include some repos likely to produce disagreement among strong models
- avoid repeating frameworks unless the repo adds a new benchmark purpose

## Intake Workflow

Use this workflow to build the candidate database.

1. Ask each model for structured suggestions.
2. Normalize repo names and deduplicate exact repeats.
3. Fetch metadata for each repo:
   - stars
   - language mix
   - archived/fork status
   - approximate size
   - license
   - recent activity
4. Reject obvious bad fits using the candidate rejection rules.
5. Group remaining repos by:
   - language
   - framework
   - topology
   - bucket
   - benchmark purpose
6. Score each candidate for:
   - distinctiveness
   - labelability
   - expected discriminative power
   - operational cost
7. Build an overfull candidate database.
8. Select the final `72` to satisfy bucket, language, size, and topology targets.

## Manual Review Questions

During final curation, ask:

- What specific failure would this repo reveal?
- Is that failure already covered by a better repo?
- Would at least one strong model likely struggle here?
- Can we label the important outputs with high confidence?
- Is the repo too easy, too noisy, or too redundant?

If the answer to the first or third question is "nothing", remove it.

## Initial Recommendation

Start with:

- one candidate-generation pass from Augur
- one from Claude
- one from Gemini
- one from DeepSeek
- optionally one from GLM-5

Then merge into a candidate database of roughly `150-250` repos and curate down to the final `72`.

The final benchmark should be human-curated even if the candidate pool is model-sourced.

## Initial Artifacts

The repo now contains first-pass sourcing artifacts:

- `references/repo-sourcing-prompt.md`
  - shared prompt for Gemini, DeepSeek, Claude, and similar models
- `references/repo-candidates/`
  - raw or lightly normalized candidate lists from individual models
- `scripts/merge_repo_candidates.py`
  - merge and dedupe helper for multi-model candidate intake

Recommended flow:

1. collect one JSON file per model under `references/repo-candidates/`
2. merge them into a single candidate pool
3. review duplicates, coverage gaps, and weak candidates
4. run a second pass with more targeted follow-up prompts
