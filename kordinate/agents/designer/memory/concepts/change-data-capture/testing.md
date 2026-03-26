---
description: Change Data Capture (CDC) — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify event emission for all DML operations and ensure consumers handle ordering, duplicates, and schema changes.

### Unit Tests

- Assert insert, update, and delete operations each produce a CDC event with correct before/after state
- Verify event ordering: updates to the same row arrive in commit order
- Test schema evolution: events with added/removed columns are handled by the consumer deserializer

### Integration Tests

- Write to the source database, consume events through the full pipeline, and verify downstream state matches
- Test initial snapshot: start a new connector and verify it captures all existing rows before streaming changes

### Failure Injection

- Kill the connector mid-stream, restart it, and verify no events are lost or duplicated beyond idempotency guarantees
