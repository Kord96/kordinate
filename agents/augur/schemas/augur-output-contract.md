# Augur Output Contract

Stable interface for accepted Augur analysis outputs.

This document describes what downstream consumers can depend on. For field-level rules, use the canonical schema files:
- [facts-schema.md](facts-schema.md)
- [atlas-schema.md](atlas-schema.md)
- [story-schema.md](story-schema.md)
- [narratives-schema.md](narratives-schema.md)
- [meta-schema.md](meta-schema.md)

## Output Layout

```text
$PROJECT_MEM/
  analysis/
    latest.json
    index.json
    by-sha/
      <commit-sha>.json
    <analysis-id>/
      meta.json
      blast.json
      facts/
        index.json
        <domain>.json
      atlas.json
      stories/
        <id>.yaml
      narratives.yaml
```

Deterministic-only runs produce:
- `blast.json`
- `facts/`
- `meta.json`

Semantic runs additionally produce:
- `atlas.json`
- `stories/`
- `narratives.yaml`

## facts/

Normalized deterministic evidence. JSON, version `"1"`. See [facts-schema.md](facts-schema.md).

Stable constraints:
- `facts/index.json` exists after deterministic analysis
- fact ids are stable and unique within a run
- every fact has provenance
- domain files may be omitted when empty
- facts are observations and candidate evidence, not final semantic conclusions

## atlas.json

Canonical semantic architecture model. JSON, version `"4"`. See [atlas-schema.md](atlas-schema.md).

Stable constraints:
- required top-level sections match `atlas-schema.md`
- component ids are kebab-case and unique
- components form a hierarchy
- top-level components should number `3-5`
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
- observation evidence uses project-relative paths

## narratives.yaml

Secondary cross-cutting reading paths over the story tree. YAML. See [narratives-schema.md](narratives-schema.md).

Stable constraints:
- `getting-started` narrative is required when semantic outputs are present
- every narrative story id exists in `stories/`
- each narrative contains `3-8` stories
- narratives may pull from any level of the story tree

## meta.json

Durable metadata record for one accepted analysis directory. See [meta-schema.md](meta-schema.md).

Stable fields:
- `project`
- `analysis_id`
- `sha`
- `commit_time`
- `analysis_mode`
- `base_sha`
- `base_commit_time`
- `blast`
- `artifacts`
- `schemas`
- `execution`
- `validation`

## What Consumers Can Assume

1. `latest.json` points only to an accepted analysis with `validation.passed = true`.
2. `analysis/index.json` provides a per-project history of accepted analyses.
3. `analysis/by-sha/<sha>.json` groups accepted analyses by analyzed commit.
4. Deterministic artifacts use `blast.json` plus `facts/`.
5. Semantic artifacts use `atlas.json`, `stories/`, and `narratives.yaml`.
6. Canonical field-level meaning lives in the schema files, not in ad hoc prompt docs.
7. New optional fields may appear, but existing stable fields do not change without a versioned schema change.
