---
description: Event Notification — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify that notifications trigger the correct consumer callbacks and that consumers fetch full state successfully.

### Unit Tests

- Assert that domain state changes emit a notification event with the correct entity ID and event type
- Verify consumers receive the notification and call back to the source API to fetch full state
- Test that consumers handle source API unavailability gracefully — retry with backoff, do not silently skip
- Assert notification payloads are minimal (ID + type) and do not leak full entity state

### Integration Tests

- Trigger a state change, verify the notification is published, and confirm the consumer fetches and processes the updated state
- Test that multiple consumers receiving the same notification each independently fetch state without interfering
- Verify that notifications for deleted entities are handled — consumer should not fail when the callback returns 404

### Ordering Tests

- Publish rapid successive notifications for the same entity and verify the consumer converges to the latest state, not an intermediate one
