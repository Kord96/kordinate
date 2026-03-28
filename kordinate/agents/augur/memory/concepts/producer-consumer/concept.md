---
description: Producer-Consumer architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [concurrency, messaging]
---
# Producer-Consumer

## Recognition

How to identify this pattern in code.

### Signatures

- Shared queue or buffer between producer and consumer threads/processes
- `put()`/`get()` or `enqueue()`/`dequeue()` calls on a shared data structure
- Bounded buffers with capacity limits, blocking on full/empty conditions
- Worker threads or processes consuming items from a queue in a loop
- Go: goroutine writing to a typed `chan` with another goroutine reading via `range` or `select` in a loop -- the chan must carry work items (not just signals)
- Java: `BlockingQueue` `put()` / `take()` with dedicated producer and consumer threads
- Python: `multiprocessing.JoinableQueue` for cross-process work queues
- Rust: `crossbeam-channel` for multi-producer multi-consumer channels
- Libraries: Python `queue.Queue`, `asyncio.Queue`, Java `BlockingQueue`

### Negative signals (not sufficient for detection)

- Go `chan struct{}` (signal-only channels) and `chan error` (error channels) are synchronization primitives, NOT producer-consumer. The pattern requires work items flowing through the channel.
- Java `java.util.function.Consumer<T>` is a functional interface, NOT the producer-consumer pattern. Same for `BiConsumer`, `IThrowableBiConsumer`.
- The words "Producer" and "Consumer" in Kafka client class names (e.g., `KafkaProducer`, `KafkaConsumer`) indicate the message-queue pattern, not in-process producer-consumer.
- Channels used only for test synchronization (e.g., `done := make(chan error, 1)`) are not this pattern.

### Confidence

- **high** -- Explicit producer threads writing to a shared `Queue` with consumer threads reading from it
- **medium** -- Async tasks feeding into a queue-like buffer consumed by separate coroutines or workers
- **low** -- Any pipeline where one component generates work and another processes it, even without a formal queue

## Architecture

Look for a shared buffer decoupling the rate of production from the rate of consumption.

### Review Checklist

- Queue is bounded to prevent unbounded memory growth under load
- Producers handle queue-full conditions (block, drop, or backpressure)
- Consumers handle empty queue gracefully (block or poll with timeout)
- Poison pill or shutdown signal exists for clean termination
- Error handling in consumers does not silently drop items

### Anti-patterns

- Unbounded queue that grows without limit when consumers fall behind
- Producer and consumer tightly coupled (direct function calls instead of queue)
- No shutdown mechanism -- threads/processes left dangling on exit
- Swallowing exceptions in the consumer loop, losing failed items permanently
