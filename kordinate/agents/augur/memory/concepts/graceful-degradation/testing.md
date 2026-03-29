---
description: Graceful Degradation — testing guidance
type: supplementary
---
## Testing

Verify that each degradation path activates correctly and provides acceptable reduced functionality.

### Unit Tests

- Simulate dependency failure and assert the degradation handler activates, returning the fallback response
- Verify the fallback response meets minimum acceptability criteria (cached data, static default, not an error)
- Test recovery: when the dependency becomes healthy again, assert the system exits degraded mode and resumes full operation
- Assert that degradation is scoped — failure of one dependency should not degrade unrelated features

### Integration Tests

- Take down a real dependency in a test environment and verify the user-facing behavior degrades gracefully rather than failing entirely
- Test cascading degradation: if a degraded feature depends on another degraded feature, verify the system remains stable
- Verify metrics and alerts fire correctly when degradation activates

### Chaos Tests

- Randomly disable dependencies and verify the system remains functional at a reduced capacity
- Simulate slow dependencies (high latency, not full failure) and verify degradation triggers based on timeout thresholds, not just connection errors
