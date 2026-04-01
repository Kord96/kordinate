---
description: Streaming flow — continuous data flow with backpressure and windowing
type: flow-shape
abstraction: [data, messaging, realtime]
---
# Streaming

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
