# Augur Analyze Skill Bundle — Core v1

This is the stable operational bundle for Augur `/analyze`.
It defines execution order, mode handling, deterministic evidence expectations, semantic output obligations, and report rules.
It should change less often than repo context and less often than semantic preload bundles.

## Cache Role

- Use this as the stable skill-prefix layer.
- Pair it with a separate memory preload bundle.
- Append repo-specific evidence and run-specific instructions last.

## Analyze Contract

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

Write the authoritative semantic atlas to `$RUN/atlas.json` following [../../schemas/atlas-schema.md](../../schemas/atlas-schema.md) v4 format. Set `version: "4"`, `generated` to today, and `metadata.analyzed_at_sha` to the current git HEAD SHA. Set `metadata.analysis_mode` to the prepared mode. In **INCREMENTAL** mode, set `metadata.affected_components` to the list of components that were re-analyzed. Set `metadata.analysis_root` to `$RUN`, `metadata.meta_path` to `$RUN/meta.json`, `metadata.base_sha` to the base analysis SHA when available, and `metadata.base_commit_time` to the base commit time when available. Atlas entries must be grounded in code inspection informed by deterministic evidence and semantic review, not emitted solely because a detector or Joern slice exists.

Use the current atlas synthesis CLI as a starting point if helpful, but the semantic phase owns the final architectural judgment:

```bash
python3 $KORDINATE_HOME/agents/augur/scripts/synthesize_atlas_from_facts.py \
  $RUN/facts \
  --project <project> \
  --output $RUN/atlas.json \
  --analysis-mode full
```

Then compose stories and narratives following [story-schema.md](story-schema.md) and [narratives-schema.md](narratives-schema.md). Use `execution-slices` facts as narrative evidence for ordered runtime paths when they are available, especially for sequencing stories inside `narratives.yaml`.

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
- every story file conforms to [story-schema.md](story-schema.md)
- `narratives.yaml` conforms to [narratives-schema.md](narratives-schema.md), including a `getting-started` narrative

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
