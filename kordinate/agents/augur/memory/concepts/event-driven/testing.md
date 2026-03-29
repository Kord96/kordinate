---
description: Event-Driven — testing guidance
type: supplementary
---
## Testing

Verify that events are published, routed, and consumed correctly, with proper handling of ordering, failures, and idempotency.

### Unit Tests

- Assert that domain actions publish the expected event type with the correct payload
- Verify consumers process events idempotently — duplicate delivery should not cause side effects
- Test event deserialization: malformed events should be rejected with a clear error, not silently dropped
- Assert that event handlers do not perform synchronous blocking calls that would stall the consumer

### Integration Tests

- Publish an event and verify the consumer processes it end-to-end, including downstream side effects
- Test event ordering: publish events with causal dependencies and verify consumers process them in the correct order
- Verify that multiple consumers on the same topic each receive and process events independently

### Failure Injection

- Kill a consumer mid-processing and verify the event is redelivered and processed successfully on restart
- Simulate broker unavailability and confirm producers either buffer events or fail with a retryable error
