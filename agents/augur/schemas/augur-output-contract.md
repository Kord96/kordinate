# Augur Output Contract

Stable interface for Augur analysis outputs.

This document describes what downstream consumers can depend on. For field-level rules, use the canonical schema files:
- [../detectors/schema.md](../detectors/schema.md)
- [observations/observations-schema.md](observations/observations-schema.md)
- [atlas-schema.md](atlas-schema.md)
- [story-schema.md](story-schema.md)
- [narratives-schema.md](narratives-schema.md)
- [meta-schema.md](meta-schema.md)

## Run-Local Working Layout

During one active analysis run, the canonical working layout is:

```text
<RUN>/
  contract.json
  blast.json
  startup.json
  index.json
  facts/
    <domain>.json
  observations/
    <artifact>.json
  derived/
    <artifact>.json
  atlas.json
  stories/
    <id>.yaml
  narratives.yaml
  log.json
```

`contract.json` is the run-local path contract. It tells the skill where the working directory, output directory, agent root, validator, and other runtime resources live for this request.

Not every run writes every semantic artifact immediately. Deterministic-only preparation may populate only:
- `contract.json`
- `blast.json`
- `startup.json`
- `index.json`
- `facts/`
- `observations/`        # optional until the semantic layer emits them
- `derived/`

Semantic work then fills in:
- `atlas.json`
- `stories/`
- `narratives.yaml`
- `log.json`

## Accepted Persisted Layout

Accepted analyses may then be persisted into the project analysis store using this layout:

```text
<PROJECT_ANALYSIS_ROOT>/
  analysis/
    index.json
    latest.json
    <commit-sha>/
      index.json
      latest.json
      <analysis-id>/
        meta.json
        blast.json
        startup.json
        index.json
        facts/
          <domain>.json
        observations/
          <artifact>.json
        derived/
          <artifact>.json
        atlas.json
        stories/
          <id>.yaml
        narratives.yaml
        log.json
        overlays/
          index.json
        reflections/
          index.json
```

Only accepted analyses should appear in the persisted layout above.

## startup.json and index.json

Run-root manifests. JSON, version `"1"` where applicable.

Stable constraints:
- `startup.json` exists after deterministic analysis
- `index.json` exists after deterministic analysis
- `startup.json` declares startup order
- `index.json` declares available fact and derived artifacts plus retrieval guidance

## facts/

Normalized deterministic evidence. JSON, version `"1"`. See [../detectors/schema.md](../detectors/schema.md).

Stable constraints:
- fact ids are stable and unique within a run
- every fact has provenance
- domain files may be omitted when empty
- facts are normalized observations, not final architecture conclusions

## observations/

Agent-authored semantic observations derived from facts plus repo inspection.

Stable constraints:
- observations are not detector output
- observations may carry confidence, questions, gaps, and recommendations
- observations do not replace `atlas.json`, `stories/`, or `narratives.yaml`
- observations are optional until the semantic layer emits them

## derived/

Deterministic semantic-planning outputs such as `component-seeds.json`, `story-seeds.json`, and `narrative-seeds.json`.

Stable constraints:
- derived artifacts live under `derived/`
- derived artifacts may use specialized JSON shapes
- derived artifacts are advisory or supporting inputs, not final semantic outputs

## atlas.json

Canonical semantic architecture model. JSON, version `"4"`. See [atlas-schema.md](atlas-schema.md).

Stable constraints:
- required top-level sections match `atlas-schema.md`
- component ids are kebab-case and unique
- components form a hierarchy
- top-level component shape should follow the preferred ranges in `atlas-schema.md`; treat them as heuristics, not rigid molds
- all cross-references resolve
- `components[].depends_on` references only component ids
- outside systems live in `external_dependencies` or `state`
- `tensions` are grounded architecture trade-offs, not generic debt backlogs
- legacy sections such as `groups`, `stack`, `debt`, `api_surface`, `security`, and `developer_experience` do not appear

## stories/

Primary navigation over the atlas. YAML files, one story per file. See [story-schema.md](story-schema.md).

Stable constraints:
- root stories mirror top-level components
- child stories refine one concern beneath a root
- story ids are unique and kebab-case
- summary is required
- story node references resolve to atlas ids
- story evidence and grounding use the path rules below

## narratives.yaml

Secondary cross-cutting reading paths over the story tree. YAML. See [narratives-schema.md](narratives-schema.md).

Stable constraints:
- `system-overview` narrative is required when full artifact outputs are present
- every narrative story id exists in `stories/`
- each narrative contains `3-8` stories
- narratives may pull from any level of the story tree

## Path Resolution Contract

All semantic artifacts should use one of these path forms when citing files:

- repo-relative paths rooted at the analyzed project, such as `pkg/server/watch.go`
- analysis-relative paths rooted at the run directory, such as `startup.json`, `facts/routes.json`, or `derived/story-seeds.json`
- absolute paths only when the runtime already emitted absolute deterministic references and they resolve correctly

Do not:
- concatenate multiple absolute paths
- guess package-local paths that do not exist
- mix repo-relative and analysis-relative semantics within one reference string

Validators and repair loops should treat these rules as the canonical path contract for full artifact outputs.

## log.json

`log.json` is a validator-owned lifecycle record for one run. The current log type is `validation`, and future log types may be added under the same neutral filename.

Stable constraints:
- one entry is appended per validation attempt
- the last iteration is the current final quality state
- issue ids stay stable for the same validator finding shape across iterations
- resolved issues remain recorded under `resolved_issues`

## meta.json

Durable metadata record for one accepted analysis directory. See [meta-schema.md](meta-schema.md).

## overlays/

Mutable user-authored layers against one concrete accepted run.

Stable constraints:
- `overlays/index.json` exists for every finalized analysis
- overlay content must not mutate the base run in place
- overlays are attached to one specific `<commit-sha>/<analysis-id>` snapshot

## reflections/

Immutable evaluations, critiques, or compare outputs attached to one accepted run.

Stable constraints:
- `reflections/index.json` exists for every finalized analysis
- reflections are distinct from overlays and do not replace generated artifacts

## What Consumers Can Assume

1. `analysis/latest.json` points only to an accepted analysis with `validation.passed = true`.
2. `analysis/index.json` provides a per-project history of accepted analyses.
3. `analysis/<sha>/index.json` groups accepted analyses by analyzed commit.
4. `analysis/<sha>/latest.json` points to the latest accepted run for that commit.
5. Deterministic run artifacts use `blast.json`, `startup.json`, `index.json`, `facts/`, and `derived/`.
6. Semantic artifacts use `observations/`, `atlas.json`, `stories/`, and `narratives.yaml`.
7. Overlay and reflection containers exist beside every accepted run even before any user edits or reviews are created.
8. Canonical field-level meaning lives in the schema files, not in ad hoc prompt docs.
9. New optional fields may appear, but existing stable fields do not change without a versioned schema change.
