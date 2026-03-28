---
description: Unit of Work architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design, data]
---
# Unit of Work

## Recognition

How to identify this pattern in code.

### Signatures

- Explicit `UnitOfWork` class or interface with `commit()`/`rollback()` controlling when changes flush
- Dirty object tracking: `register_new()`, `register_dirty()`, `register_deleted()`, change set management
- SQLAlchemy `Session` used explicitly as a unit of work (add, flush, commit across multiple repositories)
- Entity Framework `DbContext` with `SaveChanges()` coordinating multiple entity changes
- Context manager or decorator scoping a transactional boundary across multiple repository operations

**Not this pattern:** A simple database `transaction()` or `transaction.atomic()` block around a single query is standard transaction management, not the unit-of-work pattern. UoW specifically tracks dirty/new/deleted entities across multiple repositories and batches all writes into a single coordinated commit. A single-table transaction is just a transaction.

### Negative signals (not sufficient for detection)

- The word `Transaction` or `transactional` alone is NOT unit of work. Basic `@Transactional` in Spring or `db.Transaction()` in Go is standard transaction management unless paired with explicit change tracking across multiple repositories.
- `commit()` / `rollback()` on a database connection or transaction object is standard DB usage, not UoW.
- Go: `db.Begin()` / `tx.Commit()` is transaction management, not UoW. Look for explicit dirty tracking or multi-repository coordination.

### Confidence

- **high** -- explicit UoW class tracking changes across multiple repositories with `commit()`/`rollback()` controlling flush
- **medium** -- ORM session used transactionally across multiple repository calls within a single scope
- **low** -- `transaction.atomic()` or `BEGIN`/`COMMIT` blocks coordinating multiple table writes without explicit change tracking

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
