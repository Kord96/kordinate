---
description: Event-Carried State Transfer — testing guidance
type: supplementary
---
## Testing

Verify that consumers correctly build and maintain local state projections from event streams.

### Unit Tests

- Apply a sequence of events to a consumer and assert the resulting local state matches the expected projection
- Test idempotency: replaying the same event should not corrupt or duplicate local state
- Verify that events with missing optional fields are handled gracefully with defaults
- Test out-of-order delivery: consumer should either reorder or reject events that violate causality

### Integration Tests

- Publish a stream of state-carrying events and verify the consumer's local store matches the producer's authoritative state
- Test schema evolution: publish events in the old format and new format and confirm the consumer handles both
- Verify that a full replay from the event log produces the same local state as incremental consumption

### Consistency Tests

- Compare the consumer's local projection against the source of truth after a burst of concurrent updates to detect drift
