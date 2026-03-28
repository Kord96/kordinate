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
      "name": "<Human Label>",
      "description": "<optional>"
    }
  ],

  "nodes": [
    {
      "id": "<component-id>",
      "name": "<Human Readable Name>",
      "type": "service | library | worker | api | frontend | cli | store | gateway | broker | external | actor",
      "group": "<group-id>",
      "parent": "<parent-node-id | null>",
      "hasChildren": false,
      "description": "<one sentence>",
      "file": "<path/to/source>",
      "exports": ["<exported-symbol>"],
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

  "data_flows": [
    {
      "id": "<flow-id>",
      "name": "<Human Readable Flow Name>",
      "description": "<what this flow accomplishes>",
      "trigger": "<what starts it>",
      "narrative": "<scenario-driven prose, paragraphs separated by \\n\\n>",
      "narrative_map": [
        { "text": "<paragraph text>", "steps": [1, 2, 3] }
      ],
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

  "state": [
    {
      "id": "<state-id>",
      "name": "<Human Readable Name>",
      "description": "<what this state holds>",
      "purpose": "source-of-truth | cache | derived | staging",
      "technology": "<specific tool>",
      "component": "<component-id>",
      "persistence": "persistent | ephemeral",
      "narrative": "<scenario-driven prose, paragraphs separated by \\n\\n>",
      "narrative_map": [
        { "text": "<paragraph text>", "refs": ["<component-id>"] }
      ],
      "readers": ["<component-id>"],
      "writers": ["<component-id>"]
    }
  ],

  "failure_modes": [
    {
      "id": "<failure-id>",
      "trigger": "<what goes wrong>",
      "severity": "critical | high | medium | low",
      "impact": "<user-visible effect>",
      "narrative": "<scenario-driven prose, paragraphs separated by \\n\\n>",
      "narrative_map": [
        { "text": "<paragraph text>", "cascade_steps": [1, 2], "refs": ["<component-id>"] }
      ],
      "cascade": [
        { "component": "<component-id>", "effect": "<what happens>" }
      ],
      "detection": ["<signal>"],
      "recovery": ["<step>"]
    }
  ],

  "overview": "<C4 Context paragraph — what this system does, who uses it. 2-3 sentences.>",
  "structure_narrative": "<How the system is organized. 3-5 paragraphs with headings, separated by \\n\\n.>",
  "structure_narrative_map": [
    { "text": "<paragraph text>", "refs": ["<node-id>"] }
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

- `patterns` — from `patterns.md`. Array of `{ name, category }`. Detected architectural patterns for this component.
- `debt` — from `debt-assessment.md`. Object with `severity` and `items` array. Technical debt associated with this component.
- `endpoints` — from `api-review.md`. Array of `{ method, path, description }`. API endpoints exposed by this component.
- `resilience` — from `dependencies.md`. Object with boolean fields for timeout/retry/circuitBreaker and a fallback description. Resilience characteristics of external dependencies.
- `criticality` — from `dependencies.md` or `external_dependencies`. How critical this dependency is to the system.

### edges

Edges connect nodes. The `type` field distinguishes relationship kinds:

| Type | Style | Source |
|------|-------|--------|
| `depends_on` | Solid line | architecture.yaml `depends_on` arrays |
| `data_flow` | Dashed line with arrow | architecture.yaml `data_flows` steps |
| `event` | Dotted line | architecture.yaml `events` |

### data_flows

Flow objects describe data movement through the system. Each flow has ordered steps linking components.

### groups

Groups define visual clusters in the graph layout. They correspond to capabilities from architecture.yaml plus two synthetic groups:
- `external` — all external dependencies and their connections
- `actors` — all actors

The Cytoscape.js compound node feature renders groups as background containers.

## Conventions

- All `id` values match IDs from `architecture.yaml` verbatim
- `null` or missing optional fields should be omitted from the JSON (not included as `null`)
- `name` values are short (3-5 words). Detail goes in `description` fields
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
    { "id": "stream-ingestion", "name": "Stream Ingestion" },
    { "id": "batch-storage", "name": "Batch Storage" },
    { "id": "query-serving", "name": "Query Serving" },
    { "id": "external", "name": "External" },
    { "id": "actors", "name": "Actors" }
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
  "data_flows": [
    {
      "id": "ingest-to-store",
      "name": "Kafka to DuckDB Pipeline",
      "description": "The primary write path",
      "trigger": "Messages arrive on Kafka topic",
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
  "state": [
    {
      "id": "duckdb-files",
      "name": "DuckDB Storage",
      "description": "Entity data in columnar format",
      "purpose": "source-of-truth",
      "technology": "DuckDB",
      "component": "duckdb-store",
      "persistence": "persistent",
      "readers": ["query-engine"],
      "writers": ["buffer"]
    }
  ],
  "failure_modes": [
    {
      "id": "kafka-down",
      "trigger": "Kafka broker becomes unreachable",
      "severity": "critical",
      "impact": "Ingestion halts. Query serving continues from existing data.",
      "cascade": [
        { "component": "kafka-consumer", "effect": "Consumer poll fails" },
        { "component": "consume-loop", "effect": "Buffer stops receiving" },
        { "component": "buffer", "effect": "No new data to flush" }
      ],
      "detection": ["Consumer reconnection logs", "kafka_consumer_lag flatlines"],
      "recovery": ["Consumer auto-reconnects", "Buffer resumes on next poll"]
    }
  ]
}
```
