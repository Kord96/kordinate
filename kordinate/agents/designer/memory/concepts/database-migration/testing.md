---
description: Database Migration — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Validate that migrations apply cleanly, are reversible, and preserve existing data across schema transitions.

### Unit Tests

- Run each migration up and down on an empty database and verify no SQL errors
- Assert that the resulting schema matches expected table definitions, indexes, and constraints
- Test idempotency — running the same migration twice should either no-op or fail gracefully

### Integration Tests

- Seed a database with representative data, apply the migration, and verify existing rows are preserved and correctly transformed
- Test the full migration chain from the initial schema to HEAD to catch ordering or dependency issues
- Run rollback after migration and confirm the schema returns to its prior state without data corruption

### Data Safety

- Verify that destructive operations (column drops, type changes) include a backfill or data-copy step in the migration
- Test migrations against a production-sized dataset copy to catch performance issues before deploy
