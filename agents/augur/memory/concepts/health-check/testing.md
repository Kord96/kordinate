---
description: Health Check — testing guidance
type: supplementary
---
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
