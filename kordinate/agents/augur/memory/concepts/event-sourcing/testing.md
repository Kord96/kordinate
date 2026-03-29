---
description: Event Sourcing — testing guidance
---
## Testing

Ensure event replay produces consistent state and that schema evolution does not break reconstruction.

### Unit Tests

- Replay a known sequence of events and assert the resulting aggregate state matches expected values exactly
- Test snapshot + replay: load a snapshot, apply subsequent events, and verify state matches full replay from scratch
- Verify event schema versioning — apply an upcaster to a v1 event and assert it produces a valid v2 event
- Test that applying an invalid event (wrong aggregate, bad sequence number) is rejected by the aggregate

### Integration Tests

- Write events to the real event store, rebuild aggregate state, and compare against expected projections
- Test full replay from an empty state across a large event history — verify correctness and measure rebuild time
- Verify that two concurrent commands on the same aggregate produce an optimistic concurrency conflict, not corrupted state

### Failure Injection

- Corrupt a single event in the store and verify replay detects the inconsistency rather than silently producing wrong state
- Simulate event store unavailability mid-write and confirm no partial event batches are persisted
- Delete a snapshot and verify the system rebuilds state correctly from the full event history
