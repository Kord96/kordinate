---
description: CQRS — testing guidance
---
## Testing

Validate strict read/write separation, projection correctness, and behavior under eventual consistency.

### Unit Tests

- Test that commands modify only the write model — assert no side effects on the read store
- Verify projection logic: given a sequence of domain events, assert the read model reflects the correct denormalized state
- Test that queries return data exclusively from the read model, even when the write model has newer uncommitted state
- Assert that projections handle duplicate events idempotently (replaying the same event does not corrupt the read model)

### Integration Tests

- Issue a command, wait for projection sync, then query the read model and verify consistency with the write
- Rebuild the read model from scratch by replaying all events and assert it matches the incrementally projected state
- Test read model under concurrent writes — multiple commands projecting simultaneously should not produce race conditions

### Failure Injection

- Halt the projection sync process and verify the read model serves stale but valid data without errors
- Simulate projection failure mid-batch and verify it resumes from the correct offset without skipping events
- Drop and rebuild the read store while the write model is active — confirm the projection catches up fully
