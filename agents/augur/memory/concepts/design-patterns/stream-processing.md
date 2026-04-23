---
kind: concept
name: stream-processing
signatures: {}
type: pattern
abstraction:
- data
- messaging
- realtime
scope: cross-cutting
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Continuous processing over event streams rather than bounded batch inputs
- Stream operators such as map, filter, join, window, aggregate, and repartition
- Kafka Streams, Flink, Beam, Spark Structured Streaming, Reactor, or Akka Streams pipelines
- Stateful processing keyed by entity or partition
- Watermarks, windowing, or event-time semantics

### Confidence

- **high** -- explicit streaming framework or operator graph performs ongoing transformation or aggregation over ordered event streams
- **medium** -- long-running consumer pipeline transforms events continuously, but without a formal stream-processing runtime
- **low** -- one-at-a-time message consumption exists with no meaningful streaming operators or stateful processing

## Architecture

Look for continuous computation over streams, especially when ordering, windowing, and stateful aggregation shape system behavior.

### Review Checklist

- Event-time versus processing-time semantics are understood
- Stateful operators have clear partitioning and recovery strategy
- Backpressure or buffering behavior is explicit
- Late or duplicate events are handled intentionally

### Anti-patterns

- Treating ordinary queue consumers as stream-processing systems without stream semantics
- No strategy for replay, checkpointing, or state recovery
- Windowed computations that silently break under out-of-order events

### Relationship To Other Concepts

- Related to [streaming-flow](/concepts/streaming-flow) because stream processing operates over continuous flows rather than isolated requests.
- Related to [stream-to-store](/concepts/stream-to-store) when processed streams terminate in durable storage or materialized state.
- Related to [batch-processing](/concepts/batch-processing) as the main bounded-input alternative.

### Boundary

Use `stream-processing` when continuous transformation or aggregation over streams is a primary architectural concern.

Do not use it for any message consumer. The defining signal is stream-oriented computation semantics.
