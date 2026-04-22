---
kind: concept
name: streaming-flow
signatures: {}
source:
  memory_concept: memory/catalog/concepts/streaming-flow.md
type: flow-shape
abstraction:
- data
- messaging
- realtime
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

### Signatures

- Kafka consumer with continuous poll loop (not batch/cron)
- RxJS observables with `pipe()`, `map()`, `filter()`, `buffer()`
- Server-Sent Events (SSE) or WebSocket with ongoing data push
- Akka Streams, Reactor Flux, or Project Reactor with backpressure
- Kafka Streams or Flink with windowed operations (tumbling, sliding, session)
- gRPC server streaming or bidirectional streaming RPCs
- Python `async for` over an async generator or queue
- Redis Streams with `XREAD BLOCK`
- Backpressure mechanisms: buffering, dropping, throttling

### Confidence

- **high** — continuous consumer loop with backpressure handling and windowed aggregation
- **medium** — long-running consumer processing messages one at a time without explicit backpressure
- **low** — periodic polling disguised as streaming (fetch every N seconds)

### Relationship To Other Concepts

- Related to [stream-to-store](/concepts/stream-to-store) when continuous event or record streams terminate in durable storage.
- Related to [server-sent-events](/concepts/server-sent-events) as one delivery mechanism for streaming data to clients.
- Related to [pub-sub](/concepts/pub-sub) because stream-oriented systems often distribute events through publish-subscribe topologies.

### Boundary

Use `streaming-flow` when data moves continuously as an ongoing flow rather than in isolated request-response or batch interactions.

Do not use it for any long-running process or queue unless the stream semantics are architecturally central.
