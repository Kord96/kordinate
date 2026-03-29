---
description: Idempotent Consumer — testing guidance
type: supplementary
---
## Testing

Verify that duplicate messages produce the same outcome and the deduplication store behaves correctly.

### Unit Tests

- Process a message, then send the same message ID again and assert no side effects are replayed
- Verify that duplicate detection returns the original result, not an error
- Assert that the dedup check and business logic execute within the same transaction (no partial state)

### Integration Tests

- Send the same message concurrently from multiple producers and verify exactly one processing occurs
- Simulate broker redelivery (ack timeout) and confirm the consumer handles the redelivered message idempotently
- Validate TTL expiry: insert a message ID, wait past TTL, and confirm the entry is cleaned up

### Failure Injection

- Kill the consumer mid-processing and verify the message is retried and processed exactly once after restart
- Corrupt the idempotency store and verify the consumer fails visibly rather than silently reprocessing
