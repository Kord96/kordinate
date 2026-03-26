---
description: Event-Carried State Transfer architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
---
# Event-Carried State Transfer (Fat Events)

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
