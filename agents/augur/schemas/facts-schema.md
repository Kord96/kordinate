# facts.json Schema (v1)

Level 2.5 resource for Augur analysis. Facts are the stable output of deterministic extraction and the input to concept inference. They exist to decouple detector implementation details from higher-level semantic reasoning.

Pipeline:

```text
detectors -> facts -> concepts -> atlas -> stories/journeys
```

Facts are not concepts. A fact records a normalized observation about the codebase. Concepts interpret groups of facts using semantic memory, detector policy, and diagnostic questions when needed.

## Output Layout

Facts may be written as a single `facts.json` file or as a `facts/` directory containing domain files plus an index:

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
```

`index.json` is the canonical manifest. Domain files may be omitted when empty.

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
        "class": "ast | semgrep | signature | regex | manifest | question | inference",
        "framework_context": ["fastapi"],
        "status": "success | partial | skipped | failed"
      }
    ]
  },
  "facts": [
    {
      "id": "<stable fact id>",
      "kind": "framework | route | graphql-operation | grpc-service | websocket-channel | model | state-store | middleware | registration | handler | dispatch-binding | boundary | external-client | config-source | import-edge | hot-file | job | event | auth-surface",
      "domain": "<domain file name>",
      "summary": "<one sentence describing the observation>",
      "confidence": "high | medium | low",
      "framework_context": ["<framework-name>"],
      "source_files": ["<path:line>"],
      "detector": {
        "id": "<stable detector id>",
        "class": "ast | semgrep | signature | regex | manifest | question | inference",
        "strength": 1,
        "rule": "<rule id or null>",
        "bundle": "<bundle id or null>"
      },
      "raw_evidence": {
        "<key>": "<detector-specific normalized value>"
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

Detect language/runtime/framework context first. These facts narrow the search space for extractors and concept inference.

Expected `raw_evidence` keys:
- `language`
- `framework`
- `signals`
- `negative_signals`

### Routes

Capture directly observable API entrypoints. These facts feed `api_surface`, `actors`, `flows`, security concepts, and failure-mode synthesis.

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
- debt scores or recommendations

Those belong in concept inference and atlas synthesis.
