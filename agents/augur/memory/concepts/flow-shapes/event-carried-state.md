---
kind: concept
name: event-carried-state
signatures: {}
type: flow-shape
abstraction:
- messaging
- data
scope: cross-cutting
status: specialized
family: flow-shapes
---

# Explanation

Treat this as a payload-design variant under [event-driven](/concepts/event-driven), not as a separate top-level event architecture family.

Use it when the important distinction is that events carry enough state for downstream replication or projection without a callback to the source.

## Recognition

How to identify this pattern in code.

### Signatures

- Events containing full entity state, not just identifiers
- Consumers do not need to call back to the source service for data
- Larger message payloads with complete entity snapshots
- Event payloads like `{"type": "order.created", "data": {...full order object...}}`
- Eventual consistency achieved via state replication through events
- Reduced runtime coupling at the cost of larger messages and potential staleness
- Local read replicas built from consumed event data

### Confidence

- **high** -- events explicitly carry full entity state and consumers maintain local replicas without calling back
- **medium** -- events contain substantial data but consumers also make some API calls to the source
- **low** -- large event payloads that might be fat events or just verbose logging

## Architecture

Look for events carrying complete entity state that enables consumers to operate independently of the source.

### Review Checklist

- Event schema includes all fields consumers need -- no callback to the source required
- Consumers maintain local projections or caches updated from event data
- Event schema is versioned to handle additions and removals of fields over time
- Message size is monitored -- large payloads do not exceed broker limits
- Consumers handle out-of-order or duplicate events gracefully (idempotent upserts)
- Staleness is acceptable for the use case -- consumers may read slightly outdated data

### Anti-patterns

- Events so large they exceed message broker size limits or cause serialization overhead
- No schema versioning -- adding a field breaks all consumers
- Consumers treating event data as authoritative when strong consistency is required
- Including sensitive fields in fat events that propagate to services without need-to-know

### Relationship To Other Concepts

- Part of [event-driven](/concepts/event-driven) as one payload design choice within an event-driven system.
- Related to [event-notification](/concepts/event-notification) as the contrasting thin-event variant.
- Related to [change-data-capture](/concepts/change-data-capture) when downstream systems replicate state from streamed changes without callback reads.

### Boundary

Use `event-carried-state` when events intentionally carry enough state for downstream projection or replication without requesting more data from the source.

Do not promote it to a separate architecture family. It is a payload-shape distinction inside event-driven systems.
