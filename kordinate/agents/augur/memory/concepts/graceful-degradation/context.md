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

## Monitoring

Track degradation activations and dependency health so operators know when the system is running in a reduced mode.

### Key Metrics

- `degradation_active` (gauge) — boolean per feature indicating whether degraded mode is currently active
- `degradation_activations_total` (counter) — number of times degraded mode was triggered, by feature and cause
- `degradation_duration_seconds` (histogram) — how long each degradation episode lasts before recovery
- `dependency_health` (gauge) — health status of each dependency that can trigger degradation (0=down, 1=healthy)

### Alerts

- Degradation active for longer than expected recovery window (dependency not recovering)
- Multiple features degrading simultaneously (systemic issue, not isolated dependency failure)
- Degradation flapping (rapid activation/deactivation suggesting unstable dependency)

## Deployment

Verify degradation paths are functional before relying on them in production, and test them as part of every rollout.

### Rollout Implications

- Deploy degradation fallback logic before the primary path it protects — if the primary fails during rollout, the fallback must already be in place
- Rolling updates may temporarily activate degradation if new pods cannot reach a dependency the old pods could — monitor for transient degradation during rollout
- If changing degradation thresholds, deploy the new thresholds to a canary first to verify they do not trigger false activations
- Test degradation paths in staging before each production deploy — untested fallbacks fail when needed most

### Pre-deploy Checklist

- Verify all degradation fallbacks return acceptable responses (cached data, static defaults) not error pages
- Confirm alerting is active for degradation activation so operators are aware the system is running in reduced mode

