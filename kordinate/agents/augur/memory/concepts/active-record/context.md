## Testing

Test persistence behavior and domain logic independently, verifying that model instances correctly map to database rows.

### Unit Tests

- Test validation rules and domain methods without hitting the database using stubs
- Verify attribute assignment, dirty tracking, and type coercion on model instances
- Assert callbacks (before_save, after_create) fire in the correct order

### Integration Tests

- Test CRUD lifecycle against a real database: create, read, update, destroy
- Verify associations (has_many, belongs_to) load and persist correctly
- Test query scopes return expected result sets

### Failure Injection

- Simulate database connection failure during save and verify rollback behavior

