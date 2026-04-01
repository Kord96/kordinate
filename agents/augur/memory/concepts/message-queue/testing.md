---
description: Message Queue — testing guidance
type: supplementary
---
## Testing

Verify message delivery, acknowledgment semantics, and dead-letter handling under normal and failure conditions.

### Unit Tests

- Produce a message, consume it, and assert the payload matches and the message is acknowledged
- Verify that unacknowledged messages become visible again after the visibility timeout
- Assert that messages exceeding the retry limit are routed to the dead-letter queue

### Integration Tests

- Produce and consume messages through a real broker and verify end-to-end delivery
- Test consumer idempotency: redeliver a message and confirm no duplicate side effects
- Validate message ordering guarantees (FIFO or best-effort) match the queue configuration

### Failure Injection

- Kill a consumer mid-processing (before ack) and verify the message is redelivered to another consumer
- Produce a poison message that always fails processing and verify it lands in the dead-letter queue after retries
- Simulate broker unavailability and verify the producer retries or buffers messages without data loss
