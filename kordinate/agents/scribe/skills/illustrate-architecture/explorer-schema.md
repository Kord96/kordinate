# Explorer Schema: architecture.json

Level 3 resource for the illustrate-architecture skill. Defines the JSON format consumed by the Astro explorer page.

## Schema

```json
{
  "project": "<project-name>",
  "generated": "<YYYY-MM-DD>",
  "purpose": "<one sentence>",
  "stack": {
    "languages": ["<lang>"],
    "frameworks": ["<framework>"],
    "runtime": "<description>"
  },

  "groups": [
    {
      "id": "<group-id>",
      "label": "<Human Label>",
      "description": "<optional>"
    }
  ],

  "nodes": [
    {
      "id": "<component-id>",
      "label": "<Human Readable Name>",
      "type": "service | library | worker | api | frontend | cli | store | gateway | broker | external | actor",
      "group": "<group-id>",
      "parent": "<parent-node-id | null>",
      "description": "<one sentence>",
      "modules": ["<path/to/module>"],
      "patterns": [
        { "name": "<pattern-name>", "category": "<category>" }
      ],
      "debt": {
        "severity": "critical | high | medium | low",
        "items": [
          { "title": "<short title>", "description": "<detail>" }
        ]
      },
      "endpoints": [
        { "method": "GET | POST | PUT | DELETE | PATCH", "path": "</route>", "description": "<what it does>" }
      ],
      "resilience": {
        "timeout": true,
        "retry": true,
        "circuitBreaker": false,
        "fallback": "<description | null>"
      },
      "criticality": "critical | important | optional"
    }
  ],

  "edges": [
    {
      "source": "<node-id>",
      "target": "<node-id>",
      "label": "<short description>",
      "style": "solid | dashed",
      "type": "depends_on | data_flow | event"
    }
  ],

  "flows": [
    {
      "id": "<flow-id>",
      "name": "<Human Readable Flow Name>",
      "description": "<what this flow accomplishes>",
      "trigger": "<what starts it>",
      "actors": ["<actor-id>"],
      "steps": [
        {
          "component": "<component-id>",
          "action": "<verb phrase>",
          "data": "<what moves>",
          "to": "<component-id | null>",
          "technology": "<protocol>"
        }
      ]
    }
  ],

  "stores": [
    {
      "id": "<state-id>",
      "concept": "<generic term>",
      "technology": "<specific tool>",
      "component": "<component-id>",
      "stores": "<what data>",
      "purpose": "source-of-truth | cache | derived | staging",
      "persistence": "persistent | ephemeral"
    }
  ],

  "failures": [
    {
      "id": "<failure-id>",
      "trigger": "<what goes wrong>",
      "severity": "critical | high | medium | low",
      "affectedNodes": ["<component-id>"],
      "cascade": [
        { "component": "<component-id>", "effect": "<what happens>" }
      ],
      "impact": "<user-visible effect>",
      "detection": ["<signal>"],
      "recovery": ["<step>"]
    }
  ]
}
```

## Field Reference

### nodes

Every architectural entity becomes a node. The `type` field determines visual styling:

| Type | Color | Shape | Source |
|------|-------|-------|--------|
| `service` | Blue (#3B82F6) | Rounded rectangle | architecture.yaml components |
| `library` | Slate (#64748B) | Rounded rectangle | architecture.yaml components |
| `worker` | Indigo (#6366F1) | Rounded rectangle | architecture.yaml components |
| `api` | Green (#22C55E) | Rounded rectangle | architecture.yaml components |
| `frontend` | Purple (#A855F7) | Rounded rectangle | architecture.yaml components |
| `cli` | Slate (#64748B) | Diamond | architecture.yaml components |
| `store` | Amber (#F59E0B) | Cylinder | architecture.yaml state |
| `gateway` | Rose (#F43F5E) | Hexagon | architecture.yaml components |
| `broker` | Orange (#F97316) | Hexagon | architecture.yaml components |
| `external` | Red (#EF4444) | Octagon | architecture.yaml external_dependencies |
| `actor` | Teal (#14B8A6) | Ellipse | architecture.yaml actors |

### Enrichment fields

These fields are **null/empty by default** and populated only when the corresponding Designer memory file exists:

- `patterns` — from `patterns.md`. Array of `{ name, category }`. Rendered as small pill badges below the node label.
- `debt` — from `debt-assessment.md`. Object with `severity` and `items` array. Drives the colored border ring on the node (red = critical, orange = high, yellow = medium).
- `endpoints` — from `api-review.md`. Array of `{ method, path, description }`. Shown in the bottom drawer when the node is selected.
- `resilience` — from `dependencies.md`. Object with boolean fields for timeout/retry/circuitBreaker and a fallback description. Applied to external nodes.
- `criticality` — from `dependencies.md` or `external_dependencies`. Shown as a badge on external nodes.

### edges

Edges connect nodes. The `type` field distinguishes relationship kinds:

| Type | Style | Source |
|------|-------|--------|
| `depends_on` | Solid line | architecture.yaml `depends_on` arrays |
| `data_flow` | Dashed line with arrow | architecture.yaml `data_flows` steps |
| `event` | Dotted line | architecture.yaml `events` |

### flows

Flow objects are used to animate the data flow view. When a user selects a flow from the sidebar, the graph highlights the path and the bottom drawer shows the step-by-step breakdown.

### groups

Groups define visual clusters in the graph layout. They correspond to capabilities from architecture.yaml plus two synthetic groups:
- `external` — all external dependencies and their connections
- `actors` — all actors

The Cytoscape.js compound node feature renders groups as background containers.

## Conventions

- All `id` values match IDs from `architecture.yaml` verbatim
- `null` or missing optional fields should be omitted from the JSON (not included as `null`)
- Labels are short (3-5 words). Detail goes in `description` fields
- The `parent` field on nodes enables Cytoscape.js compound nodes for components with `children`
- Debt severity on a parent node is the max severity of its children
- Flow steps reference the same component IDs as nodes — this is how the explorer links graph interaction to flow animation

## Example

For the stoik stream-processing project:

```json
{
  "project": "stoik",
  "generated": "2026-03-27",
  "purpose": "Stream processing — Kafka to DuckDB with FlightSQL/HTTP serving.",
  "stack": {
    "languages": ["Python"],
    "frameworks": ["confluent-kafka", "FastAPI", "Apache Arrow Flight", "DuckDB"],
    "runtime": "Long-running Python process"
  },
  "groups": [
    { "id": "stream-ingestion", "label": "Stream Ingestion" },
    { "id": "batch-storage", "label": "Batch Storage" },
    { "id": "query-serving", "label": "Query Serving" },
    { "id": "external", "label": "External" },
    { "id": "actors", "label": "Actors" }
  ],
  "nodes": [
    {
      "id": "kafka-consumer",
      "name": "Kafka Consumer",
      "type": "worker",
      "group": "stream-ingestion",
      "description": "Connects to Kafka, polls messages in batches, deserializes with schema registry",
      "file": "stoik/stream/kafka.py",
      "patterns": [
        { "name": "stream-to-store", "category": "data" }
      ]
    },
    {
      "id": "kafka-broker",
      "name": "Kafka Broker",
      "type": "external",
      "group": "external",
      "description": "Source of streaming data",
      "resilience": {
        "timeout": true,
        "retry": true,
        "circuitBreaker": false
      },
      "criticality": "critical"
    },
    {
      "id": "upstream-kafka",
      "name": "Upstream Kafka",
      "type": "actor",
      "group": "actors",
      "description": "Produces messages to Kafka topics that stoik consumes"
    }
  ],
  "edges": [
    {
      "source": "kafka-consumer",
      "target": "buffer",
      "label": "batch records",
      "style": "solid",
      "type": "depends_on"
    },
    {
      "source": "upstream-kafka",
      "target": "kafka-consumer",
      "label": "messages",
      "style": "dashed",
      "type": "data_flow"
    }
  ],
  "flows": [
    {
      "id": "ingest-to-store",
      "name": "Kafka to DuckDB Pipeline",
      "description": "The primary write path",
      "trigger": "Messages arrive on Kafka topic",
      "actors": ["upstream-kafka"],
      "steps": [
        {
          "component": "kafka-consumer",
          "action": "Polls batch of messages",
          "data": "Raw Kafka messages -> Arrow RecordBatch",
          "to": "buffer",
          "technology": "Kafka"
        }
      ]
    }
  ],
  "stores": [
    {
      "id": "duckdb-files",
      "concept": "embedded-olap",
      "technology": "DuckDB",
      "component": "duckdb-store",
      "stores": "Entity data in columnar format",
      "purpose": "source-of-truth",
      "persistence": "persistent"
    }
  ],
  "failures": [
    {
      "id": "kafka-down",
      "trigger": "Kafka broker becomes unreachable",
      "severity": "critical",
      "affectedNodes": ["kafka-consumer", "consume-loop", "buffer"],
      "cascade": [
        { "component": "kafka-consumer", "effect": "Consumer poll fails" },
        { "component": "consume-loop", "effect": "Buffer stops receiving" },
        { "component": "buffer", "effect": "No new data to flush" }
      ],
      "impact": "Ingestion halts. Query serving continues from existing data.",
      "detection": ["Consumer reconnection logs", "kafka_consumer_lag flatlines"],
      "recovery": ["Consumer auto-reconnects", "Buffer resumes on next poll"]
    }
  ]
}
```
