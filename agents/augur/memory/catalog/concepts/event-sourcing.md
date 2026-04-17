---
description: Event Sourcing architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction:
- architectural
- data
status: primary
scope: backend
relationships:
  related_to:
  - event-driven
  - ledger
  - versioned-document
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: rich
examples: []
---
# Event Sourcing

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
