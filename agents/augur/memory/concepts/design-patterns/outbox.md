---
kind: concept
name: outbox
signatures:
  concept: outbox
  positive:
    strong:
    - outbox insert in same transaction
    - transactional outbox
    - unpublished events poller
    medium:
    - published_at
    - processed flag
    - outbox publisher
    weak:
    - stale unpublished metric
  negative:
  - publish directly to broker inside request handler
  - no durable event staging
  notes:
  - Often co-occurs with change-data-capture and idempotent-consumer.
type: pattern
abstraction:
- messaging
- data
- resilience
scope: cross-cutting
status: primary
review_questions:
  threshold: 6
  entries:
  - id: outbox-atomic-write
    prompt: Are events written to an outbox table in the same database transaction
      as the business state change?
    weight: 3
    signals:
    - outbox insert in same transaction
    - atomic write of state + event
    - transactional outbox
  - id: outbox-separate-publisher
    prompt: Does a separate process poll or stream from the outbox table to publish
      events to a message broker?
    weight: 3
    signals:
    - outbox publisher process
    - Debezium CDC on outbox
    - polling outbox for unpublished
  - id: outbox-published-marking
    prompt: Are published events marked or deleted to prevent re-publishing on the
      next poll cycle?
    weight: 2
    signals:
    - published_at timestamp set
    - processed flag updated
    - delete after publish
  - id: outbox-stale-monitoring
    prompt: Is there monitoring for stale unpublished events that may indicate a publisher
      failure?
    weight: 2
    signals:
    - alert on unpublished age
    - outbox lag metric
    - stale event monitoring
monitoring:
  applies_to:
  - component
  - flow
  health_signals:
  - name: outbox.pending.count
    description: Number of unpublished outbox rows waiting to be delivered.
  - name: outbox.max_age
    description: Age of the oldest unpublished outbox row.
  - name: outbox.publish.failure.rate
    description: Failure rate for the background publisher draining the outbox.
  business_metrics: []
  gaps:
  - Without lag and stale-age monitoring, dual-write protection exists but delivery
    failure is invisible.
family: design-patterns
---

# Explanation

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

### Relationship To Other Concepts

- Related to [change-data-capture](/concepts/change-data-capture) because outbox tables are often exported through CDC rather than polled directly.
- Related to [event-driven](/concepts/event-driven) because outbox is a reliability mechanism for event-driven delivery.
- Related to [competing-consumers](/concepts/competing-consumers) when multiple workers drain pending outbox records.

### Boundary

Use `outbox` when the architecture explicitly stages integration events in durable storage as part of the same transaction as the business write.

Do not use it for generic background jobs or in-memory event queues unless the defining guarantee is transactional event persistence before publication.
