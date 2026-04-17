---
description: Producer-Consumer architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction:
- concurrency
- messaging
status: primary
scope: cross-cutting
relationships:
  related_to:
  - competing-consumers
  - backpressure
  - message-queue
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Producer-Consumer

## Recognition

How to identify this pattern in code.

### Signatures

- Shared queue or buffer between producer and consumer threads/processes
- `put()`/`get()` or `enqueue()`/`dequeue()` calls on a shared data structure
- Bounded buffers with capacity limits, blocking on full/empty conditions
- Worker threads or processes consuming items from a queue in a loop
- Go typed `chan` with `range` over channel for consumer loops
- Java `BlockingQueue` `put()` / `take()` for bounded producer-consumer
- Python `multiprocessing.JoinableQueue` for cross-process work queues
- Rust `crossbeam-channel` for multi-producer multi-consumer channels
- Libraries: Python `queue.Queue`, `asyncio.Queue`, Java `BlockingQueue`, Go channels

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

### Relationship To Other Concepts

- Related to [competing-consumers](/concepts/competing-consumers) when multiple consumers draw work from the same source concurrently.
- Related to [backpressure](/concepts/backpressure) because producer-consumer systems often need flow control when consumers lag.
- Related to [message-queue](/concepts/message-queue) when the queue abstraction is externalized rather than in-process.

### Boundary

Use `producer-consumer` when producers and consumers are decoupled through an explicit queue, channel, or buffer boundary.

Do not use it for any asynchronous workflow. The key signal is decoupled production and consumption with a handoff buffer.
