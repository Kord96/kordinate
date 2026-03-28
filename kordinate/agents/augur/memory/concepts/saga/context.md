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

## Monitoring

Track distributed transaction outcomes and compensation events.

### Key Metrics

- `saga_completed_total` (counter) — successfully finished sagas
- `saga_failed_total` (counter) — sagas that triggered compensation
- `saga_compensation_total` (counter) — individual compensation steps executed
- `saga_duration_seconds` (histogram) — end-to-end saga duration
- `saga_step_duration_seconds` (histogram) — per-step latency to find bottlenecks

### Alerts

- Saga failure rate exceeding threshold
- Compensation failures (compensation step itself failed)
- Saga duration exceeding expected SLA
- Stuck sagas (started but neither completed nor compensated)

## Deployment

Step ordering and compensation compatibility must be maintained across old and new code versions during rollout.

### Rollout Implications

- In-flight sagas started by old code must be completable by new code — compensation logic must remain backward-compatible
- Adding or reordering saga steps during rollout requires that both old and new step orderings can reach a terminal state
- Saga state persistence format changes need migration before new code deploys — old saga records must be readable by new code
- Rolling back a saga participant service without rolling back the coordinator leaves sagas in an inconsistent state

### Pre-deploy Checklist

- Verify compensation actions for all steps are compatible across old and new code versions
- Confirm saga state store migrations are applied before deploying new coordinator logic
- Check that no long-running sagas are in a mid-step state that would be incompatible with the new step definitions
- Validate timeout values for each step still make sense with the new deployment topology

