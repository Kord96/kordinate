---
description: Audit Logging — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify every auditable action produces a complete, tamper-evident log entry with correct metadata.

### Unit Tests

- Assert each auditable operation emits a log entry with actor, action, resource, timestamp, and outcome
- Verify sensitive fields are masked or excluded from audit entries
- Test that audit entries are immutable — no update or delete path exists

### Integration Tests

- Perform CRUD operations and query the audit log to verify entries are persisted and queryable
- Test audit log search and filtering by actor, time range, and resource type
- Verify audit entries survive application restart (durable storage)

### Failure Injection

- Simulate audit store unavailability and verify the application fails closed (rejects the operation, not silently drops the log)
