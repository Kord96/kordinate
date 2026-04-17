---
description: Unit of Work architectural pattern
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
  - repository
  - aggregate
  - data-mapper
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Unit of Work

## Recognition

How to identify this pattern in code.

### Signatures

- Transaction management wrapping multiple repository operations
- Explicit `commit()` and `rollback()` methods on a unit-of-work object
- Dirty object tracking: `register_new()`, `register_dirty()`, `register_deleted()`
- SQLAlchemy `Session` used as a unit of work (add, flush, commit)
- Django `transaction.atomic()` blocks coordinating multiple saves
- Entity Framework `DbContext` with `SaveChanges()`
- Context manager or decorator scoping a transaction boundary

### Confidence

- **high** -- explicit UoW class tracking changes with `commit()`/`rollback()` controlling flush
- **medium** -- ORM session used transactionally across multiple repository calls within a single scope
- **low** -- `transaction.atomic()` or `BEGIN`/`COMMIT` blocks without explicit change tracking

## Architecture

Look for a single transactional boundary that coordinates writes across multiple repositories and flushes them atomically.

### Review Checklist

- All repository operations within a use case share the same unit of work instance
- Commit happens once at the end of the business operation, not per-repository call
- Rollback on failure reverts all changes, not just the last write
- Unit of work lifetime is scoped to the request or use case, not a singleton
- Nested units of work are either prohibited or handled with savepoints

### Anti-patterns

- Each repository managing its own transaction independently (no coordination)
- Committing inside individual repository methods instead of at the UoW boundary
- Long-lived units of work that span multiple user interactions (session leak)
- Catching exceptions inside the UoW and continuing after partial failure

### Relationship To Other Concepts

- Related to [repository](/concepts/repository) when multiple repositories share one transactional boundary.
- Related to [aggregate](/concepts/aggregate) because units of work often commit one or more aggregate changes atomically.
- Related to [data-mapper](/concepts/data-mapper) when object state changes are tracked and flushed through an explicit persistence mapping layer.

### Boundary

Use `unit-of-work` when the architecture explicitly coordinates multiple write operations through one transactional commit or rollback boundary.

Do not use it for every transaction block or ORM session unless the code clearly treats that scope as the orchestrating write boundary for a use case.
