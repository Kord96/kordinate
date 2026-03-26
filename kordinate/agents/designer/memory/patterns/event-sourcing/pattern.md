---
description: Event Sourcing architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
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

### Review Checklist

- Events are immutable facts, named in past tense (OrderPlaced, not PlaceOrder)
- Aggregate state is derived solely from replaying events — no side-channel writes
- Event schema includes a version field for future evolution
- Snapshots exist for aggregates with long event histories

### Anti-patterns

- Mutable events or events that reference other events by content
- Business logic in the event store layer
- Missing event versioning — schema changes break replay
