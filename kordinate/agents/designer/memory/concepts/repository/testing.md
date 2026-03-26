---
description: Repository — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify the repository returns domain objects, encapsulates all query logic, and is substitutable with in-memory implementations for unit tests.

### Unit Tests

- Use an in-memory repository implementation for service-layer unit tests (no database dependency)
- Verify CRUD operations: save returns the persisted entity with an assigned ID, find_by_id returns the correct entity, delete removes it
- Test query methods with multiple matching and non-matching records to verify filtering correctness
- Verify the repository returns domain objects, not ORM models or raw database rows

### Integration Tests

- Run repository methods against a real database (test container or test schema) and verify data persistence
- Test pagination: verify repositories return the correct page of results with proper ordering
- Verify bulk operations (save_all, delete_all) handle large datasets without timeouts or memory issues
- Test transaction behavior: verify rollback leaves no partial state in the database

### Interface Compliance

- Verify every repository implementation (SQL, in-memory, mock) satisfies the same interface contract
- Swap the repository implementation in integration tests and confirm service-layer behavior is identical
- Assert that no query logic leaks outside the repository (services and controllers do not construct SQL or ORM queries)
