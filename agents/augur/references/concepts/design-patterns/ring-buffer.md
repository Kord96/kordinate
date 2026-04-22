---
kind: concept
name: ring-buffer
signatures: {}
source:
  memory_concept: memory/catalog/concepts/ring-buffer.md
type: pattern
abstraction:
- data
- concurrency
scope: domain
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Fixed-size circular buffer with head and tail pointers (or read/write indices)
- Wrap-around logic using modulo arithmetic (`index % capacity`)
- `collections.deque(maxlen=N)` in Python
- Lock-free SPSC (single-producer single-consumer) or MPSC queue implementations
- Overwrite-oldest policy when buffer is full (no blocking, no resize)
- `RingBuffer`, `CircularBuffer`, `CircularQueue` class names
- Pre-allocated array with fixed capacity and no dynamic growth
- Used in logging pipelines, audio processing, network I/O buffers, LMAX Disruptor

### Confidence

- **high** -- Fixed-size buffer with modulo wrap-around, head/tail pointers, and overwrite-on-full semantics
- **medium** -- `deque(maxlen=N)` or bounded queue with FIFO eviction but no explicit ring structure
- **low** -- Fixed-size array with manual index management that may be a ring buffer

## Architecture

Look for correct bounded buffer semantics with wrap-around indexing and clear full/empty distinction.

### Review Checklist

- Buffer capacity is fixed at construction and never resized
- Full vs empty state is distinguishable (not ambiguous when head equals tail)
- Wrap-around uses modulo or bitwise AND (power-of-two sizing)
- Thread safety is addressed: either single-threaded use, lock-free atomics, or explicit locking
- Overwrite policy is intentional and documented (data loss is expected and acceptable)
- Read and write operations are O(1)

### Anti-patterns

- Resizing the buffer dynamically (defeats the purpose of bounded memory)
- No distinction between full and empty states when head equals tail
- Using a ring buffer where an unbounded queue is needed (silent data loss)
- Locking on every read/write in a hot path where a lock-free design is required

### Relationship To Other Concepts

- Related to [stream-to-store](/concepts/stream-to-store) because bounded circular buffers are common in streaming ingestion and staging paths.
- Related to [worker-pool](/concepts/worker-pool) when buffers decouple producers from pooled workers.
- Related to [backpressure](/concepts/backpressure) because ring buffers often act as bounded queues that force explicit overload behavior.

### Boundary

Use `ring-buffer` when data moves through a fixed-capacity circular buffer with wraparound indexing and bounded memory semantics.

Do not use it for any queue, deque, or cache that lacks explicit circular-buffer behavior.
