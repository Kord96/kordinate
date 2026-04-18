# Facts Schema (v1)

Level 2.5 resource for Augur analysis. Facts are the stable output of deterministic extraction and the input to concept inference. They exist to decouple detector implementation details from higher-level semantic reasoning.

Pipeline:

```text
detectors -> facts (including concept-evidence) -> atlas -> stories/narratives
```

Facts are not final semantic conclusions. A fact records a normalized observation about the codebase. Some deterministic inference outputs, such as `concept-evidence`, are still facts: they preserve candidate concept evidence without making the final semantic judgment. Final concept interpretation happens in the atlas phase.

For `concept-evidence`, deterministic output should include any run-specific semantic questions needed to confirm or reject an ambiguous candidate concept during Phase 2.

For planning-aid artifacts such as `component-seeds`, `story-seeds`, `symbols-seed`, and `state-seeds`, the contract is:
- use them to steer reading, naming, and repair
- do not treat them as final architecture truth
- prefer direct repo evidence when a seed conflicts with grounded code

## Output Layout

The canonical deterministic output is a `facts/` directory containing domain files plus an index:

```text
$MEM/
  facts/
    index.json
    frameworks.json
    routes.json
    models.json
    middleware.json
    registrations.json
    handlers.json
    dispatch-bindings.json
    boundaries.json
    external-clients.json
    config.json
    import-graph.json
    hot-files.json
    jobs.json
    events.json
    call-edges.json
    data-touches.json
    execution-slices.json
    concept-evidence.json
    story-seeds.json
    component-seeds.json
    symbols-seed.json
    state-seeds.json
    facts-guide.json
    state-access-summary.json
    control-hotspots.json
```

`index.json` is the canonical manifest. Domain files may be omitted when empty.

Observation-domain files are JSON objects containing metadata plus a top-level `facts` array. Consumers should query `file.facts`, not treat the whole domain file as a bare array.

Manifest, guide, planning-aid, and derived-structure artifacts under `facts/` may use specialized JSON shapes instead of a `facts` array. They are still deterministic normalized outputs, but they are not observation-domain files.

Some benchmark and legacy tooling may still materialize a consolidated `facts.json` payload, but the directory layout above is the source-of-truth contract for Augur analysis.

## Artifact Kinds

Use these categories when interpreting files under `facts/`:

- `observation-domain`
  - normalized detector or inference observations with a top-level `facts` array
- `manifest`
  - run-level inventory files such as `index.json` and `startup.json`
- `guide`
  - interpretation aids such as `facts-guide.json`
- `planning-aid`
  - deterministic advisory artifacts such as `story-seeds.json`, `component-seeds.json`, `symbols-seed.json`, or `state-seeds.json`
- `derived-structure`
  - deterministic summaries synthesized from lower-level facts, such as `control-hotspots.json` or `state-access-summary.json`

Do not assume every file under `facts/` uses the same JSON shape.

## Schema

```json
{
  "version": "1",
  "generated": "<YYYY-MM-DD>",
  "project": "<project-name>",
  "analysis_mode": "full | incremental | design",
  "root": "<absolute or project-relative path to scanned root>",
  "index": {
    "domains": [
      {
        "name": "routes",
        "file": "facts/routes.json",
        "count": 12
      }
    ],
    "detectors_run": [
      {
        "id": "fastapi-routes",
        "domain": "routes",
        "class": "ast | semgrep | signature | regex | manifest | question | inference | cpg",
        "framework_context": ["fastapi"],
        "status": "success | partial | skipped | failed"
      }
    ]
  },
  "facts": [
    {
      "id": "<stable fact id>",
      "kind": "framework | route | graphql-operation | grpc-service | websocket-channel | model | state-store | middleware | registration | handler | dispatch-binding | boundary | external-client | config-source | import-edge | hot-file | job | event | auth-surface | call-edge | data-touch | execution-slice | state-access-summary | control-hotspot | concept-candidate | concept-gap",
      "domain": "<domain file name>",
      "summary": "<one sentence describing the observation>",
      "confidence": "high | medium | low",
      "framework_context": ["<framework-name>"],
      "source_files": ["<path:line>"],
      "detector": {
        "id": "<stable detector id>",
        "class": "ast | semgrep | signature | regex | manifest | question | inference | cpg",
        "strength": 1,
        "rule": "<rule id or null>",
        "bundle": "<bundle id or null>"
      },
      "raw_evidence": {
        "<key>": "<detector-specific normalized value>"
      },
      "semantic_questions": {
        "enabled": true,
        "threshold": 6,
        "ask_when": ["<broad_match>"],
        "entries": [
          {
            "id": "<stable question id>",
            "prompt": "<question text>",
            "weight": 3,
            "signals": ["<signal>"]
          }
        ],
        "entry_ids": ["<stable question id>"],
        "recommended_next_step": "answer_questions | none"
      },
      "negative_evidence": ["<contradicting or confidence-reducing signal>"],
      "contradictions": ["<fact id or textual note>"],
      "relationships": {
        "component_ids": ["<component-id>"],
        "depends_on_fact_ids": ["<fact-id>"],
        "related_fact_ids": ["<fact-id>"]
      }
    }
  ],
  "metadata": {
    "analyzed_at_sha": "<git sha or null>",
    "execution_plan_version": 1,
    "bundle_versions": {
      "frameworks": "<bundle version>",
      "facts": "<bundle version>",
      "concepts": "<bundle version>"
    }
  }
}
```

## Domain Guidance

### Frameworks

Detect language/runtime/framework context first. These facts are deterministic evidence, not final semantic truth. They narrow the search space for extractors and Phase 2 interpretation.

Expected `raw_evidence` keys:
- `framework`
- `language`
- `scope`
- `framework_kind`
- `status`
- `traits`
- `relationships`
- `common_concepts`
- `common_failure_modes`
- `concepts`
- `signals`
- `negative_signals`

### Routes

Capture directly observable API entrypoints. These facts feed `actors`, `flows`, concept confirmation, and failure-mode synthesis.

Expected `raw_evidence` keys:
- `style` (`rest | graphql | grpc | websocket | sse`)
- `method`
- `path`
- `handler`
- `router`
- `auth`
- `validation`

### Models / State

Capture storage-related structures before inferring domain-model or repository concepts.

Expected `raw_evidence` keys:
- `technology`
- `entity`
- `fields`
- `relations`
- `migration_path`
- `store_purpose`

### External Clients

Capture outbound integration points before synthesizing resilience gaps or failure modes.

Expected `raw_evidence` keys:
- `technology`
- `target`
- `callsite`
- `timeout`
- `retry`
- `circuit_breaker`
- `fallback`

### Registrations / Handlers / Dispatch / Boundaries

Capture structural runtime wiring that often reveals architecture before higher-level concepts can be inferred.

Expected `raw_evidence` keys:
- Registrations:
  - `registration_type`
  - `symbol`
  - `target`
  - `runtime_role`
- Handlers:
  - `handler_type`
  - `name`
  - `target`
  - `transport`
- Dispatch bindings:
  - `binding_type`
  - `channel`
  - `producer_or_consumer`
  - `target`
- Boundaries:
  - `boundary_type`
  - `interface`
  - `implementation`
  - `storage_role`

### Import Graph / Hot Files

Capture module edges and centrality. These facts feed `module_graph`, component mapping, and blast radius.

Expected `raw_evidence` keys:
- `from`
- `to`
- `import_type`
- `fan_in`
- `fan_out`

### Call Edges

Capture deterministic caller-to-callee relationships from the Joern-backed CPG extractor. These facts strengthen flows, component dependencies, and blast-radius targeting without requiring the concept layer to read raw CPG output.

Expected `raw_evidence` keys:
- `caller_name`
- `caller_full_name`
- `caller_signature`
- `caller_file`
- `caller_line`
- `callee_name`
- `callee_full_name`
- `callee_signature`
- `call_code`
- `dispatch_type`
- `source_file`
- `line_number`
- `column_number`

### Data Touches

Capture deterministic read, write, and emit-style touch evidence from the Joern-backed CPG extractor. These facts help refine state ownership, dependency usage, and flow grounding without exposing raw CPG structure to later phases.

Expected `raw_evidence` keys:
- `owner_name`
- `owner_full_name`
- `owner_file`
- `owner_line`
- `touch_kind`
- `target_name`
- `target_full_name`
- `target_code`
- `line_number`
- `column_number`

### Execution Slices

Capture ordered call slices from the Joern-backed CPG extractor. These facts are intended to strengthen flow construction and later narrative sequencing while staying deterministic.

Expected `raw_evidence` keys:
- `slice_name`
- `slice_full_name`
- `slice_file`
- `slice_line`
- `steps`

### Concept Evidence

Capture deterministic concept candidates plus any run-specific semantic questions that Phase 2 must answer before confirming the concept in `atlas.json`.

Phase 2 should resolve each materially relevant candidate as accepted, tentative, or rejected from:
- detector backing
- contradictions
- semantic questions
- direct repo evidence

Do not let `concept-evidence` become a detector-led concept list. It is a candidate-resolution input.

Expected `raw_evidence` keys:
- `concept_id`
- `category`
- `inference_method`
- `note`
- `fingerprint`
- `supporting_fact_ids`
- `supporting_components`
- `decision_mode`
- `semantic_review_required`

Expected `semantic_questions` keys when present:
- `enabled`
- `threshold`
- `ask_when`
- `entries`
- `entry_ids`
- `recommended_next_step`
- `slice_file`
- `slice_line`
- `steps`

## Fact-to-Concept Contract

Concept inference must consume fact IDs rather than raw detector matches whenever possible.

Each detected concept in `atlas.json` should be traceable back to:
- one or more fact IDs
- detector provenance from those facts
- semantic questions asked to resolve ambiguity

Questions belong after fact extraction and before concept confirmation.

## Incremental Analysis

In incremental mode:
- re-run only extractors whose source domains were affected
- keep unchanged fact files when still valid
- update `index.detectors_run` and changed domain counts
- regenerate concepts and atlas sections only for facts in affected components plus directly impacted neighbors

## Non-Goals

Facts should not contain:
- architectural conclusions like `hexagonal`
- anti-pattern judgments like `tight-coupling`
- generic debt scores or recommendation backlogs

Those belong in concept inference and atlas synthesis.
