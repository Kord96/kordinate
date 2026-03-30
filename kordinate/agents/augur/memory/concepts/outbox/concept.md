---
description: Outbox architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [messaging, data, resilience]
---
# Outbox

## Recognition

How to identify this pattern in code.

### Signatures

- Database table named `outbox`, `outbox_events`, or `pending_events`
- Events written to the outbox table in the same transaction as the business state change
- Separate process or thread that polls the outbox table and publishes events to a message broker
- `published` / `processed` boolean flag or `published_at` timestamp column on outbox rows
- CDC (Change Data Capture) configuration reading from the outbox table (e.g., Debezium connector)
- Transaction boundaries that include both the domain write and the outbox insert

### Confidence

- **high** -- Outbox table with a publisher process, events written in the same transaction as state changes, and a `published` flag for tracking
- **medium** -- Events stored in a database table alongside business data, but the publishing mechanism is unclear or inline
- **low** -- After-commit hooks that publish events to a broker without an intermediate table (no durability guarantee)

## Architecture

Look for events persisted to a database table atomically with state changes, then relayed to a message broker by a separate process.

### Review Checklist

- Outbox insert and business state change happen in the same database transaction
- A dedicated publisher process polls or streams from the outbox table
- Published events are marked or deleted to prevent re-publishing
- Publisher handles duplicate delivery gracefully (consumers must be idempotent)
- Outbox table has an index on the unpublished/pending status for efficient polling
- Stale unpublished events are monitored and alerted on

### Anti-patterns

- Publishing events directly to the broker inside the business transaction (dual-write problem)
- No tracking of published status -- events are re-sent on every poll cycle
- Outbox table grows unbounded because published rows are never cleaned up
- Publisher and business logic share the same process with no isolation
