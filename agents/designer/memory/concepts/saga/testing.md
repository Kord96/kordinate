---
description: Saga — testing guidance
curated: true
scope: global
preloaded: none
---
## Testing

Verify that compensation chains execute correctly and that partial failures leave the system in a consistent state.

### Unit Tests

- Test each step's compensating action in isolation — assert it reverses the effect of its forward step
- Verify that compensation is idempotent: calling a compensating action twice produces the same result
- Test the saga coordinator's state machine — assert correct transitions (pending, completed, compensating, compensated)
- Assert that timeout handling triggers compensation after the configured deadline

### Integration Tests

- Run a full saga across real services and verify all steps complete and the final state is consistent
- Fail a middle step and verify all preceding steps are compensated in reverse order
- Test concurrent sagas operating on overlapping resources — verify no deadlocks or inconsistent compensation

### Failure Injection

- Kill the saga coordinator mid-execution and restart it — verify it resumes from the last recorded step state
- Simulate a compensating action failure and verify the saga retries compensation with backoff
- Introduce a step that times out and confirm the saga transitions to compensating state without waiting indefinitely
