---
name: analyze
description: >
  Semantic architecture analysis. Runtime prepares deterministic inputs and mode selection.
  Use those prepared artifacts to produce `atlas.json`, `stories/`, and `narratives.yaml`.
  Use when asked to understand architecture, audit a codebase, onboard to a project, or before
  cross-cutting changes. Use --deterministic-only for the deterministic prepass only.
argument-hint: "<project> [--reverse] [--deterministic-only]"
context: inherit
---

Produce `atlas.json`, `stories/`, and `narratives.yaml` using the prepared semantic inputs for this run.

Supports three analysis modes: **full** (first run or major changes), **incremental** (update existing atlas based on what changed), and **skip** (nothing changed). The mode is determined automatically.

## Arguments

`$ARGUMENTS` — Required: `<project>`. Optional: `[--reverse]` to scan sibling projects for inbound dependency references; `[--deterministic-only]` to produce only the deterministic prepass outputs; `[--full]` to force full analysis (ignore previous results). The runtime must provide an explicit `working_dir` for the target repo. Treat that path as the authoritative project root. If `working_dir` is missing or invalid, fail immediately instead of searching fallback repo locations.

**Memory paths:** Write durable analysis artifacts under `$AGENT_HOME_DIR/memory/projects/<project>/analysis/`. This is the canonical Augur analysis root. Keep transient job state under `$AGENT_HOME_DIR/runtime/augur/jobs/<job-id>/` when needed.

Use:
- `$PROJECT_MEM = $AGENT_HOME_DIR/memory/projects/<project>`
- `$ANALYSIS = $PROJECT_MEM/analysis`
- `$LATEST = $ANALYSIS/latest.json`
- `$RUN` exactly as provided by the runtime for this request

The runtime already prepared the deterministic analysis root for this request. Treat `$RUN` as authoritative. Do not recompute `$RUN`, do not guess or override `AGENT_HOME_DIR`, and do not rerun `prepare_analysis_dir.py` or other setup scripts unless the prepared paths are obviously missing or inconsistent with the current `working_dir`.

Start from the prepared artifacts, not from general repo orientation:
- Do not run `git status`, `git rev-parse`, or other Git discovery commands during normal semantic analysis.
- Do not list the repo root or scan unrelated top-level directories unless `$RUN` is missing or clearly inconsistent.
- First inspect, in order: `$RUN/blast.json`, `$RUN/facts/`, `$RUN/facts/concept-evidence.json`, and any existing `$RUN/atlas.json`.
- Only widen into repo files after those prepared artifacts identify what still needs semantic judgment.
- If the prepared artifacts are missing or inconsistent, fail clearly instead of improvising a different setup flow.

Structured outputs live in the durable analysis directory for the analyzed commit: `$RUN`. Keep one canonical `meta.json` inside each analysis directory. `latest.json` is only a convenience pointer to the most recent accepted analysis directory.

---

## Semantic Phase

The runtime prepares:
- `$RUN/blast.json`
- `$RUN/facts/`
- `$RUN/facts/concept-evidence.json`
- the analysis mode: `full | incremental | skip`
- for incremental runs, a prior accepted analysis referenced by `base_analysis_dir`

Use those inputs as assisting evidence. They inform your semantic understanding but do not fully constrain it.

Use `$RUN/blast.json` to decide semantic investigation scope:
- If `mode=full`: investigate the whole project.
- If `mode=incremental`: start from the accepted base analysis referenced by `base_analysis_dir`, then focus semantic investigation on `changed_files` plus the affected blast slice (`affected_components`, `affected_flows`, `affected_state`, `affected_dependencies`, `affected_concepts`).
- If `mode=skip`: do not continue into Phase 2.

Do not default to broad repo exploration when `blast.json` already provides a targeted incremental slice. Expand beyond the blast slice only when the code you inspect shows the semantic boundary is larger than the deterministic estimate.

Preferred semantic sequence:
1. Read `$RUN/blast.json`.
2. Read the relevant files in `$RUN/facts/`, especially `frameworks.json`, `concept-evidence.json`, and any domain files named by the blast slice.
3. Read any existing `$RUN/atlas.json` as a draft or baseline, then correct it from evidence.
4. Read only the repo files needed to resolve ambiguity, verify claims, or ground specific atlas/story/narrative content.
5. Write outputs under `$RUN`.

Write the authoritative semantic atlas to `$RUN/atlas.json` following [../../schemas/atlas-schema.md](../../schemas/atlas-schema.md) v4 format. Set `version: "4"`, `generated` to today, and `metadata.analyzed_at_sha` to the current git HEAD SHA. Set `metadata.analysis_mode` to the prepared mode. In **INCREMENTAL** mode, set `metadata.affected_components` to the list of components that were re-analyzed. Set `metadata.analysis_root` to `$RUN`, `metadata.meta_path` to `$RUN/meta.json`, `metadata.base_sha` to the base analysis SHA when available, and `metadata.base_commit_time` to the base commit time when available. Atlas entries must be grounded in code inspection informed by deterministic evidence and semantic review, not emitted solely because a detector or Joern slice exists.

Use the current atlas synthesis CLI as a starting point if helpful, but the semantic phase owns the final architectural judgment:

```bash
python3 $KORDINATE_HOME/agents/augur/scripts/synthesize_atlas_from_facts.py \
  $RUN/facts \
  --project <project> \
  --output $RUN/atlas.json \
  --analysis-mode full
```

Then compose stories and narratives following:
- `$KORDINATE_HOME/agents/augur/skills/analyze/story-schema.md`
- `$KORDINATE_HOME/agents/augur/skills/analyze/narratives-schema.md`

Do not guess alternate schema locations such as `/app/schemas/...`.
Use `execution-slices` facts as narrative evidence for ordered runtime paths when they are available, especially for sequencing stories inside `narratives.yaml`.

Coverage requirements during semantic work:
- dependencies: internal modules, imports, external services, infra manifests, inter-service config
- API surface: routes, interfaces, boundary behavior, framework-native expectations
- components and groups: 5-10 top-level components, 3-5 groups, nested children where needed
- actors and flows: 2-4 critical flows, grounded in code
- domain model and state: core data shape, stores, readers, writers, persistence model
- health and debt: failure modes, instrumentation gaps, anti-patterns, prioritized recommendations

Write narrative artifacts under:
- `$RUN/stories/`
- `$RUN/narratives.yaml`

This phase is required unless `--deterministic-only` was explicitly passed. Before validation, confirm that:
- `$RUN/stories/` exists and contains story `.yaml` files
- `$RUN/narratives.yaml` exists
- atlas `metadata.story_ids` reflects the composed stories when applicable
- every story file conforms to `$KORDINATE_HOME/agents/augur/skills/analyze/story-schema.md`
- `narratives.yaml` conforms to `$KORDINATE_HOME/agents/augur/skills/analyze/narratives-schema.md`, including a `getting-started` narrative

### Refine

Review each story. If a summary makes a claim not directly observed in Phase 1, re-read the specific source file(s) to verify or correct it. Only re-read files that an ungrounded claim references.

### Validate

Run the shared validation protocol against your output. **You need a completion token to finish.**

Run the validator script directly with the analysis directory:

```bash
python3 $KORDINATE_HOME/agents/augur/skills/analyze/scripts/validate_output.py $RUN
```

The validator returns either errors or a completion token.

If validation returns errors: read them, fix the output files inside `$RUN`, and run the validator again. Repeat until it returns a **completion token**. Record it.

When validation passes:
- update `$ANALYSIS/latest.json` to point at `$RUN`
- keep `$RUN` as durable history
- use the latest accepted analysis pointer for later requests

### Evaluate

With validated output, run quality checks:

1. **Groundedness**: for each observation with `grounded_in` references, re-read the cited source files and verify the claim holds. The code is ground truth, not the atlas. Target: >= 0.85.

2. **Coverage**: critical atlas nodes in at least one story / total critical nodes. Target: >= 0.80.

3. If groundedness is low, fix claims. If coverage is low, add stories. Always revalidate after changes.

---

## Report

```
## Analysis: <project>

**Mode**: full | incremental (N of M components) | skip
**Purpose**: <one sentence>
**Components** (N): <names>
**Groups** (N): <names>
**Flows** (N): <names>
**Concepts**: N patterns, N anti-patterns, N gaps
**API**: N endpoints, N critical / N recommended / N minor findings
**Debt**: Score N — Grade X. <interpretation>
**External** (N): <names with criticality>
**Failures** (N): <names with severity>
**Facts**: N total across <domain list>
**Stories**: N root, N child
**Narratives** (N): <titles> (if any)
**Groundedness**: <min>-<max> across stories
**Coverage**: <percentage> of critical components
**Validation token**: <token from validate-output>
**Top recommendations**: 1. ... 2. ... 3. ...

Written to:
  snapshot: <path>
  facts: <path> (domain files)
  atlas: <path>
  stories: <path> (N files)
  narratives: <path> (single YAML index, if any)
  current: <path>
```

If `--deterministic-only`, omit Atlas/Stories/Narratives/Groundedness/Coverage lines. If `mode=skip`, report that the existing accepted analysis was reused.
