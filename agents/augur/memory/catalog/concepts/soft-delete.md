---
description: Soft Delete architectural pattern
type: pattern
testable: true
graphable: true
abstraction: [data]
---
# Soft Delete

## Recognition

How to identify this pattern in code.

### Signatures

- `deleted_at` timestamp column that is NULL for active records and set on deletion
- `is_deleted` boolean flag on database tables or document models
- Default query scopes that add `WHERE deleted_at IS NULL` to all reads
- `paranoid: true` (Sequelize), `acts_as_paranoid` (Rails), `SoftDeletes` trait (Laravel)
- `restore()` or `undelete()` method alongside the soft delete operation
- Unique index constraints that include the `deleted_at` column to allow re-creation of deleted records
- Scheduled hard-delete or purge jobs that permanently remove records past a retention period

### Confidence

- **high** -- `deleted_at` column with default query scope excluding deleted records and a `restore()` method
- **medium** -- `is_deleted` boolean flag referenced in query conditions across the codebase
- **low** -- Records marked with a status field (`status = 'archived'`) that are filtered from default queries

## Architecture

Look for consistent application of soft delete scopes across all queries and clear lifecycle for eventual hard deletion.

### Review Checklist

- Default query scopes exclude soft-deleted records so developers cannot accidentally return them
- A mechanism exists to query deleted records explicitly when needed (admin views, audit, restore)
- Unique constraints account for soft-deleted records (composite index with `deleted_at` or partial index)
- Foreign key relationships handle soft-deleted parents correctly (cascading soft delete or preventing it)
- A retention policy and purge job exist to hard-delete records past the retention period
- Soft delete is applied consistently across related entities (deleting a parent soft-deletes children)

### Anti-patterns

- Queries throughout the codebase manually adding `WHERE deleted_at IS NULL` instead of using a default scope
- No purge strategy, causing tables to grow unbounded with deleted records degrading query performance
- Unique constraints that break when re-creating a record with the same natural key as a soft-deleted one
- Soft-deleting a parent while leaving orphaned child records in an active state
