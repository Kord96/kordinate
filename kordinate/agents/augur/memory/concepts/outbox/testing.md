---
description: Outbox — testing guidance
type: supplementary
---
## Testing

Verify atomicity of the outbox write, publisher delivery guarantees, and correct cleanup behavior.

### Unit Tests

- Insert a business entity and outbox event in one transaction, then verify both are committed or both rolled back on failure
- Verify the publisher marks events as published after successful broker delivery
- Test idempotent re-publishing: re-running the publisher on already-published events does not produce duplicates on the broker
- Assert unpublished events are fetched in insertion order (FIFO guarantee)

### Integration Tests

- Write an event, run the publisher, and verify the message appears on the broker topic with correct payload and headers
- Simulate broker unavailability: verify events remain in the outbox unpublished and are retried on recovery
- Test the cleanup job: published events older than the retention window are deleted without affecting unpublished events
- Verify CDC-based publishing (if used) picks up new outbox rows within the expected latency window

### Failure Injection

- Kill the publisher mid-batch and verify no events are lost (at-least-once delivery) and the next run resumes correctly
- Simulate a database connection failure during publish and verify the publisher retries without marking events as published
