---
kind: concept
name: stream-to-store
signatures: {}
source:
  memory_concept: memory/catalog/concepts/stream-to-store.md
type: pattern
abstraction:
- data
- integration
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Kafka consumer imports (`kafka.KafkaConsumer`, `confluent_kafka.Consumer`)
- `consumer.poll()` / `consumer.commit()` calls managing offset lifecycle
- Buffered writes accumulating records before flushing to a store
- `flush()` callbacks triggered by buffer size or time thresholds
- `stoik` imports for stream processing integration
- Consumer group configuration (`group.id`, `auto.offset.reset`, `enable.auto.commit=false`)
- Offset management logic committing only after successful store writes
- Flink sink connectors writing stream data to external stores (`SinkFunction`, `RichSinkFunction`)

### Confidence

- **high** -- Kafka consumer with `poll()`/`commit()` and explicit offset management after buffered `flush()` to a store, or Flink sink connectors
- **medium** -- Consumer group configs with `enable.auto.commit=false` and buffered writes, but without explicit flush callbacks
- **low** -- Stream consumer reading from a broker without clear buffer-then-flush mechanics or offset commit ordering

## Architecture

Look for correct offset management — commits only after successful flush.

### Review Checklist

- Offsets are committed after the store write succeeds, not before
- Buffer has both size and time-based flush triggers
- Flush failures trigger retry with backoff before giving up
- Consumer group rebalancing is handled without data loss or duplication
- Store writes are idempotent (safe to replay on reprocessing)

### Anti-patterns

- Auto-commit enabled — offsets advance regardless of flush success
- Unbounded buffer with no size limit (memory exhaustion on slow stores)
- No dead-letter handling for permanently unprocessable messages

### Relationship To Other Concepts

- Related to [data-pipeline](/concepts/data-pipeline) because stream-to-store is one continuous ingestion form of data pipeline.
- Related to [message-queue](/concepts/message-queue) when streams or broker records are the source being drained into storage.
- Related to [materialized-view](/concepts/materialized-view) when the store acts as a continuously updated projection optimized for queries.

### Boundary

Use `stream-to-store` when a continuous stream of records is consumed and persisted into a store or projection as an architectural pipeline.

Do not use it for any ETL or batch write path. The key signal is continuous streamed ingestion into storage.
