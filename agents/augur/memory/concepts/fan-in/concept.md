---
description: Fan-in flow — parallel results converge into a single aggregation point
type: flow-shape
abstraction: [data, integration]
---
# Fan-In

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
