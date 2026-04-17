---
description: Aggregate Root architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- design
- data
status: primary
scope: backend
relationships:
  related_to:
  - ddd
  - repository
  - value-object
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: rich
examples: []
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

See also: ddd

### Relationship To Other Concepts

- Related to [ddd](/concepts/ddd) because aggregates are one of the central tactical DDD patterns.
- Related to [repository](/concepts/repository) when repositories persist and retrieve aggregates as consistency units.
- Related to [value-object](/concepts/value-object) because aggregates often compose immutable value objects inside their boundary.

### Boundary

Use `aggregate` when the codebase clearly models a consistency boundary around one root entity controlling invariants and child mutations.

Do not use it for any large domain object or object graph. A root entity with children is not automatically an aggregate unless it is also the transactional and invariant boundary.
