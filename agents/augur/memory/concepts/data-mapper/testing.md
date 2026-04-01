---
description: Data Mapper — testing guidance
type: supplementary
---
## Testing

Verify that mapping logic correctly translates between domain objects and persistence representations without leaking either concern.

### Unit Tests

- Map a domain entity to a persistence row and assert all fields are correctly translated, including type conversions
- Map a persistence row back to a domain entity and verify no data loss or silent truncation
- Test null/missing field handling — mapper should apply defaults or raise explicit errors, never silently drop data
- Verify that domain invariants hold after a round-trip: entity -> row -> entity produces an equivalent object

### Integration Tests

- Insert via mapper, read back via mapper, and compare with the original domain object
- Test mapping of associated/nested entities to verify join or embedded document handling
- Verify that schema changes (added/removed columns) are caught by mapper tests rather than surfacing as runtime errors
