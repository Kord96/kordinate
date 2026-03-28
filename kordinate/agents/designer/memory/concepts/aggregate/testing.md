---
description: Aggregate Root — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Test invariant enforcement at the aggregate boundary and verify that all mutations go through the root.

### Unit Tests

- Assert business invariants are enforced: invalid state transitions raise domain errors
- Verify the root coordinates child entity mutations — direct child modification is not possible
- Test that domain events are emitted for each state change on the aggregate

### Integration Tests

- Persist and reload an aggregate, verifying all child entities and value objects round-trip correctly
- Test optimistic concurrency: concurrent modifications to the same aggregate produce a conflict error
- Verify repository loads the full aggregate in a single consistency boundary

### Failure Injection

- Attempt to violate invariants under concurrent load and verify no inconsistent state is persisted
