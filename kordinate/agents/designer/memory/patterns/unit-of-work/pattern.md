---
description: Unit of Work architectural pattern
curated: true
scope: global
preloaded: none
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
