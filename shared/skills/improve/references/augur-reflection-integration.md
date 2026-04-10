# Augur Reflection Integration

Design for making runtime reflections a first-class part of the benchmark and improve loop.

## Problem

`shared/klaude-daemon` can generate and publish reflections, but reflections do not currently appear to have:

- durable benchmark storage
- a restore path into later runs
- aggregation across runs
- explicit consumption by `/improve`

Without those pieces, reflections are mostly write-only telemetry.

## Goal

Use reflections as a structured post-run feedback channel that helps:

- capture repo-specific architectural lessons
- surface transferable detector improvements
- preserve raw evidence from analyze runs
- feed `/improve` analysis with evidence
- compare model strengths, weaknesses, overlap, and complementarity over time

Reflections should support evaluation and detector improvement. They should not replace hard scoring.

## Reflection Roles

Separate reflection into two roles.

### 1. Run reflection

Per-run notes attached to a specific analyze execution.

Use for:

- repo-specific architectural observations
- misleading naming or layout traps
- useful detection signals
- candidate grep, AST, or question improvements

### 2. Durable memory reflection

Cross-run lessons worth carrying into future work.

Use for:

- stable lessons about detector behavior
- repeated grounding or interpretation pitfalls
- recurring repo-pattern failures
- prompt or detector improvements that generalize

Only a subset of run reflections should be promoted into durable memory.

## Reflection Storage

Every analyze run with reflection enabled should save a reflection artifact on disk.

Reflections should be stored under Augur-owned paths whether or not `/improve` is active.

Recommended root:

```text
/kord/augur/memory/projects/<repo>/reflections/
```

Recommended subdirectories:

```text
/kord/augur/memory/projects/<repo>/reflections/
  runs/
  summaries/
  promoted/
```

Use:

- `runs/`
  - append-only raw per-run reflections
- `summaries/`
  - derived aggregation outputs
- `promoted/`
  - distilled durable lessons intentionally kept

In addition to repo-local raw storage, build a normalized global index:

```text
/kord/augur/memory/global/reflections/
  records/
  manifest.json
  summaries/
```

Use:

- `records/`
  - normalized global copies of raw reflection records, optimized for filtering and comparison
- `manifest.json`
  - lightweight counts by model and repo
- `summaries/`
  - global cross-project reflection summaries

Per-run location:

```text
/kord/augur/memory/projects/<repo>/reflections/runs/<reflection-id>.json
```

This should be written directly from the runtime response rather than relying only on Kafka topic retention.

### Reflection ID

Every reflection should have a stable run identifier.

Recommended format:

```text
<timestamp>__<owner>--<repo>__<sha-short>__<model>__<memory-bundle>__<skill-bundle>__run-<n>
```

Example:

```text
2026-04-09T12-00-00Z__microsoft--vscode__abc1234__augur__selective__holistic__run-1
```

## Reflection Record Schema

Recommended stored record:

```json
{
  "reflection_id": "2026-04-09T12-00-00Z__microsoft--vscode__abc1234__augur__selective__holistic__run-1",
  "repo": "owner/name",
  "pinned_sha": "abc123",
  "model": "augur",
  "provider": "openai",
  "runtime_kind": "codex-sdk",
  "memory_bundle": "selective",
  "skill_bundle": "holistic",
  "run_number": 1,
  "analysis_mode": "full",
  "correlation_id": "job-123",
  "reflection": {
    "project": "...",
    "general": "..."
  },
  "captured_at": "ISO-8601"
}
```

## Recommended Reflection Prompt

The default daemon reflection prompt is too generic for benchmark use. For benchmark runs, use a custom reflection prompt asking for structured evaluation insight.

Recommended prompt location:

- `agents/augur/skills/analyze/reflection-prompt.md`

Target output should remain strict JSON, but the text should answer these questions:

- What architectural conventions were specific to this repo?
- What naming or layout choices could mislead shallow analysis?
- What signals actually helped identify concepts or component boundaries?
- What false-positive traps appeared?
- What grep signatures, AST rules, or diagnostic questions should Augur add or refine?

## Reflection Payload Evolution

Current daemon payload is:

```json
{
  "project": "...",
  "general": "..."
}
```

This is enough to start if we standardize the contents around repo-specific and transferable detector lessons.

Longer term, the payload should grow structured optional fields:

```json
{
  "project": "...",
  "general": "...",
  "detector_signals": ["plugin registration via config array"],
  "false_positive_traps": ["service folder used for thin adapters only"],
  "next_actions": ["add grep or AST support for job registry patterns"]
}
```

If changing daemon types is too expensive immediately, encode these sections in text first and parse later.

## Improve Loop Integration

`/improve` dataset benchmark mode should consume reflections explicitly.

`/improve reflection --from-runs` should also treat stored reflections as a comparative dataset rather than just isolated run notes.

### During a run

After each run:

1. capture the reflection payload from the runtime response
2. store it under the Augur reflection root
3. include its path and `reflection_id` in the run manifest

### During aggregation

Build or refresh the normalized global index first, then build reflection summaries across runs:

- recurring detector ideas
- recurring false-positive traps
- recurring repo-pattern lessons
- repeated repo-specific failures
- contradictions between reflection and numeric score
- consensus suggestions across models
- unique suggestions by model
- complementarity and overlap between model pairs

Recommended output:

```text
/kord/augur/memory/projects/<repo>/reflections/summaries/<summary-id>.json
```

and for cross-project work:

```text
/kord/augur/memory/global/reflections/summaries/<summary-id>.json
```

### During analysis

The `/improve` analyzer should read:

- scorecards
- grading outputs
- blind comparison results
- reflection summary

and produce:

- probable causes of poor performance
- candidate detector changes
- candidate prompt or bundle changes
- repos that need better labels or different evaluation criteria
- model-specific strengths and blind spots
- whether models are redundant or complementary on the current dataset

## Reflection Aggregation Rules

Aggregate by:

- model
- memory bundle
- skill bundle
- repo
- language
- bucket

Look for:

- repeated detector opportunities
- repeated mentions of the same misleading pattern
- repeated notes about ungrounded or weakly supported concepts
- repeated evidence that specific repo shapes break current heuristics

Do not aggregate by counting every free-text phrase literally. Normalize to tags or short categories where possible.

## Raw vs Derived Artifacts

Keep a strict separation:

- raw reflections
  - immutable, append-only, one per run
- derived summaries
  - recomputable aggregations
- promoted lessons
  - deliberate curated outputs

`/improve` should never rewrite raw reflection records.

It may generate:

- summary files
- promotion candidates
- improve reports

But raw reflections should remain the source evidence.

## Promotion To Memory

Do not automatically write every reflection into long-term memory.

Promote only when a lesson is:

- repeated across multiple repos or runs
- stable across models or bundle settings
- actionable in future evaluations

Examples worth promoting:

- `holistic memory improves component coverage on large monorepos`
- `story grounding is the most common failure source on giant repos`
- `selective skill underreports failure modes for worker-heavy systems`

Examples not worth promoting:

- `repo X timed out once`
- `run 2 had noisy logs`
- `this one repo is weird`

## Suggested File Layout

Add these locations under Augur-owned workspace memory:

```text
/kord/augur/memory/projects/<repo>/reflections/
  runs/
  summaries/
  promoted/
```

Recommended outputs:

- per-run reflection record
- aggregated reflection summary
- promoted durable lessons file

## Suggested Reflection Summary Schema

```json
{
  "summary_id": "2026-04-09-core-suite-1",
  "generated_at": "ISO-8601",
  "source_reflection_ids": [],
  "by_model": {},
  "by_memory_bundle": {},
  "by_skill_bundle": {},
  "by_repo": {},
  "common_detector_signals": [
    {"tag": "job-registry-pattern", "count": 12}
  ],
  "common_false_positive_traps": [
    {"tag": "service-folder-thin-adapters", "count": 7}
  ],
  "promotion_candidates": [
    "Add detector support for plugin registration through exported config arrays."
  ]
}
```

## Operational Recommendation

Start with the simplest path:

1. capture reflection from runtime response
2. store it under the Augur reflection root
3. aggregate reflections into one summary file
4. feed that summary into `/improve` analysis

Only after this is working should you:

- extend daemon reflection schema
- add Kafka consumers
- auto-promote lessons to memory

This keeps the integration useful early without requiring infrastructure-first work.
