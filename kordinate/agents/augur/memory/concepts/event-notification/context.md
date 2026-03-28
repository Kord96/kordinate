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

## Deployment

Coordinate notification infrastructure so consumers can fetch full state from the source when notified.

### Rollout Implications

- Deploy the source API changes before the notification schema changes — consumers call back to the source for full data, so the API must serve the new shape first
- Thin events carry minimal payload, so schema changes are less risky than fat events, but routing and type identifiers must remain stable
- Rolling consumer updates may cause brief windows where some consumers fetch old API versions — ensure the source API supports both
- If changing the notification channel (topic rename, new routing key), deploy consumers listening on both old and new channels during transition

### Pre-deploy Checklist

- Verify the source API is healthy and can handle the callback load that notifications will trigger
- Confirm notification topic/exchange exists with correct routing in the target environment

