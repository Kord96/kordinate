## Testing

Verify that health endpoints accurately reflect application and dependency state under all conditions.

### Unit Tests

- Assert liveness endpoint returns 200 when the process is healthy, independent of dependency state
- Assert readiness endpoint returns 503 when any critical dependency is unreachable
- Verify that individual dependency checks have their own timeouts and do not hang the health endpoint

### Integration Tests

- Bring down a dependency (database, cache) and confirm the readiness endpoint transitions to unhealthy
- Restore the dependency and verify the readiness endpoint recovers within the expected window
- Validate that health endpoints are not exposed on public-facing ports or are properly authenticated

### Failure Injection

- Introduce latency on a dependency check exceeding the probe timeout and verify the probe reports failure, not a hang
- Simulate a slow-starting application and confirm the startup probe keeps the pod alive until ready

## Monitoring

Track probe outcomes and dependency health to detect degraded service before users are affected.

### Key Metrics

- `health_check_status` (gauge) — current health state per endpoint (0=down, 1=degraded, 2=up)
- `health_check_duration_seconds` (histogram) — latency of health endpoint responses
- `readiness_probe_failures_total` (counter) — readiness failures triggering traffic removal
- `dependency_health_status` (gauge) — per-dependency connectivity state checked by readiness

### Alerts

- Readiness probe failing for longer than one probe interval (pod removed from service)
- Liveness probe failing (pod restart imminent)
- Health check latency exceeding probe timeout (false failures likely)
- Dependency health degraded across multiple pods simultaneously

## Deployment

Ensure probes are tuned for the rollout strategy and slow-starting services do not get killed prematurely.

### Rollout Implications

- Configure startup probes for slow-starting applications to prevent liveness failures during initialization
- Set `initialDelaySeconds` on readiness probes so new pods are not expected to serve traffic before startup completes
- Rolling updates should wait for readiness before proceeding to the next pod (maxUnavailable and maxSurge tuning)
- Verify that liveness probes do not check external dependencies -- a database outage should not restart all pods

### Pre-deploy Checklist

- Confirm probe timeouts are shorter than probe periods to avoid overlapping checks
- Validate that readiness probe failure removes the pod from the Service endpoint list without killing it
- Test that a new deployment rolls back automatically when readiness probes fail consistently

