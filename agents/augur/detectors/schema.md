# Canonical Facts Schema

This is the canonical schema for Augur normalized facts.

Facts are deterministic normalized records produced by detector infrastructure.
They are not semantic observations, architectural conclusions, planning hints,
or model-authored judgments.

If a record needs confidence, semantic uncertainty, or recommendations, it
belongs in `observations/`, not `facts/`.

## Responsibilities

Keep these responsibilities separate:

- deterministic extraction lives under `detectors/`
- normalized fact files are emitted into run-local `facts/`
- semantic interpretation happens after fact extraction
- semantic observations belong in `observations/`

## Detector Source Layout

```text
detectors/<domain>/
  policy.yaml
  signatures.yaml
  ast-grep.yaml       # optional
  semgrep.yaml        # optional
```

Special families:

```text
detectors/frameworks/<name>/
detectors/concepts/
  policy.yaml
  ast-grep/<name>.yaml
  semgrep/<name>.yaml
  signatures/<name>.yaml
```

During migration, concept loaders may also read legacy per-concept directories:

```text
detectors/concepts/<name>/
  policy.yaml
  ast-grep.yaml
  semgrep.yaml
  signatures.yaml
```

Typed concept assets take precedence over legacy per-concept files when both
exist for the same detector id.

Use ordinary `<domain>` directories for normalized fact domains such as
`routes`, `models`, or `events`.

Concept and framework meaning lives in `memory/concepts/`. Frameworks are one
semantic family inside that tree.

Shared executable helpers and detector runners live under:

```text
detectors/utils/
```

## Run Output Layout

The canonical deterministic output uses run-root manifests plus a dedicated
`facts/` directory:

```text
<RUN>/
  contract.json
  blast.json
  startup.json
  index.json
  facts/
    <domain>.json
  derived/
    <artifact>.json
```

Common fact domains include:
- `frameworks.json`
- `routes.json`
- `handlers.json`
- `dispatch-bindings.json`
- `boundaries.json`
- `external-clients.json`
- `config.json`
- `hot-files.json`
- `call-edges.json`
- `data-touches.json`
- `execution-slices.json`
- `concepts.json`
- `symbols-seed.json`
- `state-seeds.json`
- `state-access-summary.json`
- `control-hotspots.json`
- `health-candidates.json`
- `failure-scenario-candidates.json`

`startup.json` and `index.json` are run manifests, not fact files.

`derived/` contains deterministic planning artifacts that are not facts, such as
`component-seeds.json`, `story-seeds.json`, and `narrative-seeds.json`.

## Top-Level Fact Domain Shape

Each file under `facts/` is a JSON object with metadata plus a top-level
`facts` array.

```json
{
  "version": "1",
  "generated": "<YYYY-MM-DD>",
  "project": "<project-name>",
  "analysis_mode": "full | incremental | design",
  "domain": "<domain-name>",
  "detectors": {},
  "count": 0,
  "facts": []
}
```

Domain files may be omitted when empty.

## Fact Record Shape

A fact is one deterministic record with normalized detector provenance.

```json
{
  "id": "<stable fact id>",
  "fact": {
    "<normalized detector fields>": "<value>"
  },
  "detector_id": "<stable detector id>",
  "source_files": ["<path:line>"],
  "notes": []
}
```

### Required constraints

- `id` is stable within a run
- `fact` is the canonical normalized detector payload
- `detector_id` points to file-level detector metadata
- `source_files` points to concrete repo evidence when applicable
- `fact` preserves detector-specific deterministic detail
- `notes` is optional and may hold deterministic detector-side caveats, but not
  semantic conclusions

### Not allowed in facts

- semantic confidence
- accepted / tentative / rejected verdicts
- recommendations
- architectural explanations
- semantic entity mappings

## File-Level Detector Metadata

Each fact domain file should include a `detectors` object keyed by detector id.
This is where detector metadata lives.

```json
{
  "detectors": {
    "<detector id>": {
      "id": "<detector id>",
      "kind": "<emitted fact kind or subtype>",
      "class": "source | aggregate | bridge | ast | semgrep | signature | regex | manifest | cpg",
      "strength": 1,
      "rule": "<rule id or null>",
      "bundle": "<bundle id or null>",
      "docs": ["<repo-relative markdown path>"],
      "review_questions": ["<deterministic follow-up question>"]
    }
  }
}
```

`docs` and `review_questions` are detector metadata, not per-fact metadata.
They help downstream consumers interpret a class of facts without repeating the
same links on every record.

## Detector Metadata

Detectors should declare their emitted kinds in `policy.yaml`.

```yaml
domain: <kebab-case domain id>
emits:
  - <fact kind>
frameworks:
  include: []
  exclude: []
policy:
  emit_threshold: 1 | 2 | 3 | 4 | 5
  fallback_order:
    - cpg
    - ast_grep
    - semgrep
    - signatures
    - manifest
normalization:
  fact_kind: <kind>
  required_fields: []
  optional_fields: []
```

## Guidance

Fact detectors should be:
- narrow
- framework-native where useful
- easy to benchmark independently
- deterministic in both extraction and emission

Examples:
- route extractor emits route facts
- ORM extractor emits model and state-store facts
- import graph extractor emits import-edge and hot-file facts
- higher-level detectors may emit aggregate facts such as control hotspots or
  state-access summaries, as long as they remain deterministic
