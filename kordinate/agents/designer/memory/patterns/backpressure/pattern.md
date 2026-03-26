---
description: Backpressure architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
---
# Backpressure

## Recognition

How to identify this pattern in code.

### Signatures

- `Flowable` or `Observable` with `onBackpressure*` operators (RxJava)
- `asyncio.Queue(maxsize=)` with bounded capacity (Python)
- `BoundedChannel` from Rust tokio for capacity-limited async channels
- `BlockingQueue` with explicit capacity (Java `ArrayBlockingQueue`, `LinkedBlockingQueue(capacity)`)
- Kafka consumer configuration with `max.poll.records` limiting batch size
- `reactor.core.publisher.Flux` with backpressure operators (`limitRate`, `onBackpressureBuffer`, `onBackpressureDrop`)
- Go channel with explicit buffer size (`make(chan T, N)`) used for flow control

### Confidence

- **high** -- explicit backpressure operators (`onBackpressureDrop`, `onBackpressureBuffer`, `limitRate`) with bounded queues and rejection/drop policies
- **medium** -- bounded queues or channels with capacity limits but no explicit backpressure signaling to the producer
- **low** -- unbounded queues with consumer lag monitoring but no active flow control mechanism

## Architecture

Flow control mechanism for when a producer is faster than its consumer. Prevents memory exhaustion and queue overflow by signaling the producer to slow down or by shedding load. Common strategies include rate limiting, bounded queues with rejection, and reactive pull-based consumption.
