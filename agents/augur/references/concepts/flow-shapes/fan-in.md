---
kind: concept
name: fan-in
signatures: {}
source:
  memory_concept: memory/catalog/concepts/fan-in.md
type: flow-shape
abstraction:
- data
- integration
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

### Signatures

- `Promise.all()` or `asyncio.gather()` collecting parallel results
- Map-reduce: map phase fans out, reduce phase fans in
- Scatter-gather: request sent to N services, responses aggregated
- Barrier/join patterns: wait for all N tasks before proceeding
- Kafka consumer reading from multiple partitions into one handler
- `CompletableFuture.allOf()` in Java collecting concurrent results
- Go `sync.WaitGroup` or channel-based fan-in collecting goroutine results
- GraphQL DataLoader batching multiple individual requests into one query
- Aggregation service that calls multiple backends and merges responses

### Confidence

- **high** — explicit parallel dispatch with barrier/join collecting all results before proceeding
- **medium** — sequential calls to multiple services with results merged at the end
- **low** — multiple data sources queried but aggregation is ad-hoc, not structured

### Relationship To Other Concepts

- Related to [scatter-gather](/concepts/scatter-gather) because gather phases often terminate in a fan-in point.
- Related to [mapreduce](/concepts/mapreduce) because many reduce stages are specialized fan-in points over distributed work.
- Related to [data-pipeline](/concepts/data-pipeline) because pipelines often narrow multiple sources into one processing stage.

### Boundary

Use `fan-in` when the architectural shape is many upstream paths converging into one downstream stage or consumer.

Do not use it for ordinary dependency graphs or any place where two functions merely call a shared helper.
