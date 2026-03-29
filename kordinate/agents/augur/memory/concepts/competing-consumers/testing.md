---
description: Competing Consumers — testing guidance
type: supplementary
---
## Testing

Verify messages are processed exactly once across consumers and that work distributes evenly.

### Unit Tests

- Publish N messages with M consumers and assert each message is processed exactly once
- Verify message acknowledgment: unacknowledged messages are redelivered to another consumer
- Test idempotency: redelivered messages do not produce duplicate side effects

### Integration Tests

- Run multiple consumer instances against a real broker and verify even work distribution
- Test consumer group rebalancing: add/remove a consumer mid-stream and verify no messages are lost or duplicated

### Failure Injection

- Kill a consumer mid-processing and verify the message is redelivered to a surviving consumer
- Introduce a poison message and verify it routes to a DLQ after max retries without blocking the queue
