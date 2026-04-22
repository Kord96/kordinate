---
kind: concept
name: change-data-capture
signatures: {}
source:
  memory_concept: memory/catalog/concepts/change-data-capture.md
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

- Database log tailing (WAL, binlog, oplog)
- Debezium connector configurations
- WAL readers (`wal2json`, `pgoutput`, `test_decoding`)
- Binlog consumers (Maxwell, Canal)
- `source.connector.class=io.debezium` in connector configs
- Outbox table polling as a CDC alternative
- Event sourcing derived from database changes rather than application events

### Confidence

- **high** -- Debezium connector config or WAL/binlog reader setup with downstream event publishing
- **medium** -- Outbox table with a polling mechanism or trigger-based change capture
- **low** -- Database triggers that write to a separate events table without explicit CDC framing

## Architecture

Look for database change streams being captured and published as events to downstream consumers.

### Review Checklist

- CDC connector tracks its position (LSN/offset) durably to survive restarts without data loss
- Schema evolution is handled (schema registry or compatible deserialization)
- Ordering guarantees are preserved per-key/per-table through the pipeline
- Tombstone/delete events are propagated correctly, not silently dropped
- Connector lag is monitored with alerts for growing replication delay
- Snapshot strategy is defined for initial load and connector recovery

### Anti-patterns

- Polling the source table with timestamps instead of using the database log (misses deletes, has clock skew)
- No schema evolution strategy, causing downstream deserialization failures on ALTER TABLE
- Ignoring connector offset management, leading to duplicate or lost events on restart
- Capturing all tables indiscriminately instead of targeting specific tables that need change events

### Relationship To Other Concepts

- Related to [event-sourcing](/concepts/event-sourcing) because both create downstream event streams, but CDC derives them from database changes rather than domain events.
- Related to [search-index](/concepts/search-index) when CDC feeds indexing or denormalized search projections.
- Related to [cqrs](/concepts/cqrs) when CDC is the mechanism that keeps read models synchronized with a write store.

### Boundary

Use `change-data-capture` when the system explicitly tails database changes or outbox-like persistence changes and republishes them downstream.

Do not use it for generic event publishing, webhook delivery, or ordinary domain events unless the defining mechanism is database change capture.
