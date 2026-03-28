# architecture.yaml Schema

Level 3 resource for the architect skill. Defines the output format.

## Schema

```yaml
version: "1"
generated: "<YYYY-MM-DD>"
project: "<project-name>"

purpose: "<one sentence — what the system does>"

stack:
  languages: ["<Python>", "<TypeScript>"]
  frameworks:
    - name: "<framework name>"
      concepts: ["<concept-name>"]         # which concepts from the catalog this framework provides
  runtime: "<description of how it runs>"

actors:
  - id: "<kebab-case>"
    type: user | service | cron | cli | data-source | external
    description: "<what they do with the system>"

capabilities:
  - id: "<kebab-case>"
    description: "<business-level, not technical>"
    actors: ["<actor-id>"]
    components: ["<component-id>"]

components:
  - id: "<kebab-case>"
    name: "<Human Readable Name>"
    description: "<what it does — one sentence>"
    type: service | library | worker | api | frontend | cli | scheduler | store | gateway | broker | database
    modules:
      - "<path/to/module>"
    depends_on: ["<component-id>"]
    patterns: ["<pattern-name>"]        # optional, from detect-patterns
    deployment:                          # optional, for deployment viewpoint
      namespace: "<k8s namespace>"
      kind: "<Deployment | StatefulSet | CronJob | Pod>"
      replicas: <count>
      node: "<node name or selector>"
    children:                            # optional, recursive — same schema as parent
      - id: "<kebab-case>"
        name: "<Human Readable Name>"
        description: "<one sentence>"
        type: "<same types as parent>"
        modules: ["<path>"]
        depends_on: ["<component-id>"]
        children: [...]                  # can nest further

data_flows:
  - id: "<kebab-case>"
    actors: ["<actor-id>"]              # which actors trigger this flow
    name: "<Human Readable Flow Name>"
    description: "<what this flow accomplishes>"
    trigger: "<what starts it>"
    steps:
      - component: "<component-id>"
        action: "<verb phrase>"
        data: "<what moves>"
        to: "<component-id>"           # omit for terminal step
        technology: "<protocol or transport: HTTP/JSON | gRPC | Kafka topic | localStorage | in-memory>"  # optional

state:
  - id: "<kebab-case>"
    concept: "<generic: relational-db | document-store | embedded-olap | cache | object-store | message-broker | filesystem | in-memory>"
    technology: "<specific: PostgreSQL | DuckDB | Redis | etc.>"
    component: "<component-id>"
    stores: "<what data>"
    purpose: source-of-truth | cache | derived | staging
    persistence: persistent | ephemeral

events:
  - id: "<kebab-case>"
    type: topic | signal | webhook | cron | pubsub
    name: "<topic.name or event name>"
    producer: "<component-id>"
    consumers: ["<component-id>"]
    data: "<what the event carries>"

external_dependencies:
  - id: "<kebab-case>"
    name: "<Human Readable Name>"
    concept: "<generic: http-api | dns | smtp | nfs | grpc | database>"
    technology: "<specific if known>"
    component: "<component-id>"
    purpose: "<why needed>"
    criticality: critical | important | optional
    resilience:
      timeout: true | false
      retry: true | false
      circuit_breaker: true | false
      fallback: "<description or null>"

failure_modes:
  - id: "<kebab-case>"
    trigger: "<what goes wrong>"
    cascade:                               # ordered sequence of what breaks
      - component: "<component-id>"
        effect: "<what happens to this component>"
    impact: "<what end users experience>"
    detection:                             # ordered: how you know it happened
      - "<first signal — metric, log, error, or 'none'>"
      - "<second signal>"
    recovery:                              # ordered: what happens to recover
      - "<first recovery step — automatic or manual>"
      - "<second recovery step>"
    severity: critical | high | medium | low
```

## Conventions

- All `id` fields are kebab-case, unique within their section
- Cross-references use `id` strings, not indices
- `concept` fields use generic infrastructure terms, `technology` fields name the specific tool
- Components should number 5-10 for most projects. If you have more than 12, you're probably not abstracting enough. If you have fewer than 4, you're probably over-abstracting.
- Data flows trace the critical paths, not every possible code path. 2-4 flows for a typical project.
- Failure modes should cover every external dependency and every stateful component. The question is always: "what happens if this goes down?"
- Components can nest to any depth via `children`. Each level represents a meaningful architectural boundary (service → package → module). Don't nest deeper than the code's natural structure.
- The `deployment` field on components enables the deployment viewpoint. Only add it to components that map to a k8s workload.
- The `technology` field on flow steps enables annotated sequence diagrams. Use short labels: "HTTP/JSON", "gRPC :8815", "Kafka", "localStorage".

## Example

A complete example for a stream-processing pipeline project:

```yaml
version: "1"
generated: "2026-03-26"
project: "stoik"

purpose: "Stream processing framework — consumes from Kafka, buffers in memory, flushes to DuckDB, serves via FlightSQL and HTTP."

stack:
  languages: ["Python"]
  frameworks:
    - name: "confluent-kafka"
      concepts: [message-queue, stream-to-store, pub-sub]
    - name: "FastAPI"
      concepts: [router, middleware, input-validation]
    - name: "Apache Arrow Flight"
      concepts: [grpc]
    - name: "DuckDB"
      concepts: [embedded-olap]
    - name: "stoik"
      concepts: [stream-to-store, backpressure, retry]
  runtime: "Long-running Python process with consumer loop, embedded DuckDB, and FlightSQL/HTTP servers"

actors:
  - id: upstream-kafka
    type: data-source
    description: "Produces messages to Kafka topics that stoik consumes"
  - id: query-client
    type: service
    description: "Queries stored data via FlightSQL (gRPC) or HTTP API"
  - id: ops
    type: user
    description: "Monitors health via Prometheus /metrics endpoint"

capabilities:
  - id: stream-ingestion
    description: "Consume messages from Kafka and buffer them for batch processing"
    actors: ["upstream-kafka"]
    components: ["kafka-consumer", "buffer"]
  - id: batch-storage
    description: "Flush buffered data to DuckDB with staging tables and merge"
    actors: []
    components: ["buffer", "duckdb-store"]
  - id: query-serving
    description: "Serve stored data via FlightSQL and HTTP with caching"
    actors: ["query-client"]
    components: ["flight-server", "http-api", "cache"]

components:
  - id: kafka-consumer
    name: "Kafka Consumer"
    description: "Connects to Kafka, polls messages in batches, deserializes with schema registry"
    type: worker
    modules: ["stoik/stream/kafka.py"]
    depends_on: ["buffer"]
    patterns: ["stream-to-store"]
  - id: buffer
    name: "In-Memory Buffer"
    description: "Accumulates records and triggers flush on size or time threshold"
    type: library
    modules: ["stoik/buffer.py"]
    depends_on: ["duckdb-store"]
  - id: consume-loop
    name: "Consume Loop"
    description: "Orchestrates the consumer-buffer-store lifecycle with heartbeat management"
    type: service
    modules: ["stoik/loop.py"]
    depends_on: ["kafka-consumer", "buffer", "duckdb-store"]
  - id: duckdb-store
    name: "DuckDB Store"
    description: "Writes Arrow batches to DuckDB via staging tables, handles lock contention with retry"
    type: store
    modules: ["stoik/storage/duckdb.py"]
    depends_on: []
    patterns: ["retry"]
  - id: flight-server
    name: "FlightSQL Server"
    description: "Serves SQL queries over Arrow Flight gRPC protocol"
    type: api
    modules: ["stoik/server/flight.py", "stoik/server/proxy.py"]
    depends_on: ["duckdb-store"]
  - id: http-api
    name: "HTTP API"
    description: "FastAPI server providing REST access to cached entity data"
    type: api
    modules: ["stoik/server/api.py"]
    depends_on: ["cache", "flight-server"]
    children:
      - id: api-server
        name: "API Server"
        description: "Serves REST endpoints for entity queries"
        type: api
        modules: ["stoik/server/api.py"]
        depends_on: ["cache"]
      - id: cache-warmer
        name: "Cache Warmer"
        description: "Pre-fetches entity data into cache on startup"
        type: worker
        modules: ["stoik/server/cache.py"]
        depends_on: ["flight-server"]
  - id: cache
    name: "Entity Cache"
    description: "LRU cache with warm-up that pre-fetches entity data via FlightSQL"
    type: library
    modules: ["stoik/server/cache.py", "stoik/server/flight_pool.py"]
    depends_on: ["flight-server"]

data_flows:
  - id: ingest-to-store
    actors: ["upstream-kafka"]
    name: "Kafka to DuckDB Pipeline"
    description: "The primary write path — messages flow from Kafka through buffer to DuckDB"
    trigger: "Messages arrive on Kafka topic"
    steps:
      - component: kafka-consumer
        action: "Polls batch of messages, deserializes via schema registry"
        data: "Raw Kafka messages → Arrow RecordBatch"
        to: buffer
      - component: buffer
        action: "Accumulates records until size/time threshold reached"
        data: "Arrow RecordBatch"
        to: duckdb-store
      - component: duckdb-store
        action: "Inserts into staging table, merges into base table"
        data: "Arrow RecordBatch → DuckDB rows"

  - id: query-path
    actors: ["query-client"]
    name: "Query Serving Path"
    description: "The read path — clients query via FlightSQL or HTTP"
    trigger: "Client sends SQL query or HTTP request"
    steps:
      - component: http-api
        action: "Receives HTTP request, checks cache"
        data: "HTTP request"
        to: cache
      - component: cache
        action: "Returns cached result or delegates to FlightSQL"
        data: "Cache key → Arrow table"
        to: flight-server
      - component: flight-server
        action: "Executes SQL against DuckDB, returns Arrow stream"
        data: "SQL query → Arrow RecordBatch stream"

state:
  - id: duckdb-files
    concept: embedded-olap
    technology: DuckDB
    component: duckdb-store
    stores: "Entity data (nodes, edges, aggregations) in columnar format"
    purpose: source-of-truth
    persistence: persistent
  - id: entity-cache
    concept: in-memory
    technology: "Python LRU dict"
    component: cache
    stores: "Pre-fetched entity lookup results"
    purpose: cache
    persistence: ephemeral

events:
  - id: kafka-ingest
    type: topic
    name: "Configured at runtime per consumer instance"
    producer: upstream-kafka
    consumers: ["kafka-consumer"]
    data: "Avro-encoded entity records"

external_dependencies:
  - id: kafka-broker
    name: "Kafka Broker"
    concept: message-broker
    technology: "Apache Kafka (KRaft)"
    component: kafka-consumer
    purpose: "Source of streaming data"
    criticality: critical
    resilience:
      timeout: true
      retry: true
      circuit_breaker: false
      fallback: null
  - id: schema-registry
    name: "Schema Registry"
    concept: http-api
    technology: "Confluent Schema Registry"
    component: kafka-consumer
    purpose: "Avro schema resolution for deserialization"
    criticality: important
    resilience:
      timeout: false
      retry: false
      circuit_breaker: false
      fallback: null

failure_modes:
  - id: kafka-down
    trigger: "Kafka broker becomes unreachable"
    cascade:
      - component: kafka-consumer
        effect: "Consumer poll fails, reconnection loop starts"
      - component: consume-loop
        effect: "Buffer stops receiving records"
      - component: buffer
        effect: "No new data to flush, buffer empties"
    impact: "Ingestion halts. No new data written to DuckDB. Query serving continues from existing data."
    detection:
      - "Consumer reconnection logs (librdkafka)"
      - "kafka_consumer_lag metric flatlines"
    recovery:
      - "Consumer auto-reconnects with librdkafka backoff"
      - "Buffer resumes on next successful poll"
      - "No data loss — offsets not committed until flush"
    severity: critical
  - id: duckdb-lock-contention
    trigger: "Multiple processes contend for DuckDB file lock"
    cascade:
      - component: duckdb-store
        effect: "Write operations block waiting for file lock"
    impact: "Write latency increases. Buffer grows in memory."
    detection:
      - "Retry count metrics in duckdb_store"
    recovery:
      - "Exponential backoff retry (60 attempts, jitter)"
    severity: medium
  - id: snapshot-module-missing
    trigger: "Store.release() called with snapshot=True"
    cascade:
      - component: duckdb-store
        effect: "ModuleNotFoundError raised during snapshot"
    impact: "ModuleNotFoundError — process crashes"
    detection:
      - "none"
    recovery:
      - "none"
    severity: high
```
