---
kind: concept
name: event-sourcing
signatures:
  concept: event-sourcing
  positive:
    strong:
    - aggregate replay from events
    - append-only event store
    - event stream append operations
    medium:
    - past-tense event classes
    - snapshot repository
    weak:
    - history table with replay-like semantics
  negative:
  - state mutated directly with no event replay model
  notes:
  - AST rules are available for this concept and can be auto-confirming when combined
    with strong semantic evidence.
type: pattern
abstraction:
- architectural
- data
scope: backend
status: primary
review_questions:
  threshold: 6
  entries:
  - id: event-sourcing-replay-derived-state
    prompt: Is aggregate state derived solely by replaying an append-only sequence
      of events?
    weight: 3
    signals:
    - apply methods on aggregates that mutate state from events
    - load_events and replay to reconstruct state
  - id: event-sourcing-append-only-store
    prompt: Are events stored in an append-only event store or stream?
    weight: 3
    signals:
    - EventStore or EventStream with append_events
    - EventStoreDB client or append-only table
  - id: event-sourcing-past-tense-events
    prompt: Are events named as immutable past-tense facts?
    weight: 2
    signals:
    - OrderPlaced
    - PaymentReceived
  - id: event-sourcing-snapshots
    prompt: Do snapshots exist for aggregates with long event histories?
    weight: 1
    signals:
    - Snapshot class
    - snapshot repository
    - snapshot interval configuration
monitoring:
  applies_to:
  - component
  - flow
  health_signals:
  - name: event_store.append.latency
    description: Latency for appending new events to the store or stream.
  - name: projection.lag
    description: Delay between event append and read-model projection completion.
  - name: replay.duration
    description: Time required to rebuild aggregate state from historical events.
  business_metrics: []
  gaps:
  - Missing projection lag or replay duration metrics hides read-side staleness and
    recovery cost.
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `EventStore` or `EventStream` classes managing append-only event persistence
- `append_events()` / `load_events()` methods on repositories or stores
- Axon Framework imports (`org.axonframework.eventsourcing`)
- EventStoreDB client usage or connection configuration
- `apply()` methods on aggregate classes that mutate state from events
- Event upcasting logic that transforms old event versions to new schemas
- `Snapshot` classes or snapshot repository interfaces for aggregate state caching
- Events named in past tense (`OrderPlaced`, `PaymentReceived`) as immutable facts

### Confidence

- **high** -- EventStore/EventStream classes with `append_events()` and `load_events()`, or Axon/EventStoreDB imports with aggregate `apply()` methods
- **medium** -- Snapshot classes alongside event replay logic, or event upcasting transformations
- **low** -- Past-tense named event classes without clear append-only storage or replay mechanics

## Architecture

Look for correct event modeling and state reconstruction.

### Relationship To Other Concepts

- `event-sourcing` is the persistence model: append-only events are the source of truth and state is reconstructed from replay.
- Use `event-driven` for communication semantics between components when replay-based persistence is not the key idea.
- Use `ledger` for financial balancing and account invariants.
- Use `versioned-document` for document history without treating the whole aggregate model as an event stream.

### Review Checklist

- Events are immutable facts, named in past tense (OrderPlaced, not PlaceOrder)
- Aggregate state is derived solely from replaying events — no side-channel writes
- Event schema includes a version field for future evolution
- Snapshots exist for aggregates with long event histories

### Anti-patterns

- Mutable events or events that reference other events by content
- Business logic in the event store layer
- Missing event versioning — schema changes break replay

### Boundary

Do not use `event-sourcing` for any system that emits events. Prefer it only when replayable event history is the authoritative persistence model.

### Relationship To Other Concepts

- Related to [event-driven](/concepts/event-driven) because event sourcing usually participates in an event-driven architecture, though it is specifically a persistence model rather than just a communication style.
- Related to [ledger](/concepts/ledger) when an append-only record of events forms the authoritative history.
- Related to [versioned-document](/concepts/versioned-document) when historical versions are preserved, though event sourcing rebuilds current state from events rather than storing successive document snapshots.
