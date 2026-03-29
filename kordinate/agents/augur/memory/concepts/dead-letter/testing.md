---
description: Dead Letter Queue — testing guidance
type: supplementary
---
## Testing

Verify that messages land in the DLQ only after retry exhaustion and that replay mechanisms work correctly.

### Unit Tests

- Simulate a message that fails processing and assert it is routed to the DLQ after the configured retry count
- Verify that transient errors trigger retries but do not immediately DLQ the message
- Assert DLQ messages retain the original payload plus failure metadata (error reason, attempt count, timestamp)

### Integration Tests

- Publish a poison message, verify it arrives in the DLQ, replay it after fixing the consumer, and confirm successful processing
- Test that DLQ replay preserves message ordering when order matters downstream
- Verify DLQ depth metrics increment correctly as messages are enqueued

### Failure Injection

- Inject a serialization error and confirm the message is dead-lettered rather than silently dropped
- Simulate a full DLQ (capacity limit) and verify the system applies backpressure or alerts rather than losing messages
