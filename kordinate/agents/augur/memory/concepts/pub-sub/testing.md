---
description: Publish-Subscribe — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify fan-out delivery, subscriber isolation, and correct behavior under failure and duplicate delivery.

### Unit Tests

- Publish a message and verify all registered subscribers receive it with the correct payload
- Subscribe and unsubscribe a handler, then publish and verify the unsubscribed handler is not called
- Verify subscriber failure does not block delivery to other subscribers on the same topic
- Test message filtering: subscribers with topic filters receive only matching messages

### Integration Tests

- Publish through the real broker (Kafka, Redis, NATS) and verify end-to-end delivery to a test subscriber
- Test at-least-once delivery: acknowledge a message, then verify it is not redelivered; nack a message and verify redelivery
- Verify ordering guarantees per partition or subject (where the broker guarantees ordering)
- Publish during a subscriber restart and verify no messages are lost (retained or replayed from offset)

### Idempotency Tests

- Deliver the same message twice and verify the subscriber produces the correct outcome (no duplicate side effects)
- Simulate broker redelivery after ack timeout and verify the subscriber handles it gracefully
