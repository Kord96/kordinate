---
description: Aggregate Root architectural pattern
curated: true
scope: global
preloaded: none
---
# Aggregate Root

## Recognition

How to identify this pattern in code.

### Signatures

- `AggregateRoot` or `AggregateBase` base class / mixin
- Root entity class that holds references to child entities (e.g., `Order` containing `OrderLine` list)
- All mutations on children go through the root's methods, never directly
- Invariant checks (guard clauses) inside root methods before modifying state
- Repository interface returns only the root entity, never child entities alone
- Domain events raised from within the aggregate root after state changes

### Confidence

- **high** -- Explicit `AggregateRoot` base class, repository loads/saves only roots, child entity constructors are internal/protected
- **medium** -- Root entity that owns a collection of child entities with mutator methods, but no formal base class
- **low** -- A "god object" that holds many child references but exposes setters on children directly

## Architecture

Look for a consistency boundary where one root entity controls all mutations to its children.

### Review Checklist

- All state changes on child entities pass through the root's public methods
- Invariants are enforced at the aggregate level before persisting
- Repository loads and saves the entire aggregate as a unit
- References between aggregates use IDs, not direct object references
- Aggregate boundaries are small enough to avoid contention
- Domain events are raised after successful state transitions, not before

### Anti-patterns

- Child entities expose public setters that bypass the root
- Aggregates reference other aggregates by object pointer instead of ID
- Single aggregate spans too many entities, causing lock contention on writes
- Business rules split between the aggregate and the service layer
