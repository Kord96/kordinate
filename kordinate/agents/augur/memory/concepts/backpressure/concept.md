---
description: Backpressure architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [resilience, concurrency]
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
- Go channel with explicit buffer size (`make(chan T, N)`) used for flow control where producer blocks or drops on full channel
- Java: LMAX Disruptor `WaitStrategy` (`BusySpinWaitStrategy`, `BlockingWaitStrategy`) controlling producer-consumer flow
- Java: Reactive Streams `Subscription.request(n)` for demand-driven flow control
- Go: `maxConcurrency` or `maxInFlight` configuration limiting parallel processing as flow control
- Go: `select` with `default` on channel send to implement non-blocking backpressure (drop on full)
- Any: `prefetchCount`, `maxPollRecords`, `maxInFlight` configuration in message broker consumers

### Negative signals (not sufficient for detection)

- The word "backpressure" in comments, documentation, or variable names without actual flow control implementation is not this pattern
- A bounded `BlockingQueue` or buffered channel used simply as a work queue (producer-consumer) without explicit backpressure signaling to the producer is producer-consumer, not backpressure
- TCP flow control at the transport layer is not application-level backpressure
- Python: `Semaphore` or `BoundedSemaphore` used for concurrency limiting (e.g., limiting concurrent HTTP requests) is rate-limiting or connection-pooling, not backpressure unless the semaphore is used to signal the producer to slow down
- Python: `asyncio.Queue(maxsize=N)` used as a simple work queue without producer-side awareness of queue fullness is producer-consumer, not backpressure

### Confidence

- **high** -- explicit backpressure operators (`onBackpressureDrop`, `onBackpressureBuffer`, `limitRate`) with bounded queues and rejection/drop policies
- **medium** -- bounded queues or channels with capacity limits but no explicit backpressure signaling to the producer
- **low** -- unbounded queues with consumer lag monitoring but no active flow control mechanism

## Architecture

Flow control mechanism for when a producer is faster than its consumer. Prevents memory exhaustion and queue overflow by signaling the producer to slow down or by shedding load. Common strategies include rate limiting, bounded queues with rejection, and reactive pull-based consumption.
