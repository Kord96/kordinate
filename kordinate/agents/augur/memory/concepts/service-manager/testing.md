---
description: Service Manager — testing guidance
curated: true
scope: global
preloaded: none
---
## Testing

Validate startup ordering, graceful shutdown behavior, and health check accuracy under real conditions.

### Unit Tests

- Test startup sequencing: assert that dependency checks pass before the service signals readiness
- Verify health check accuracy: inject a degraded dependency and assert the readiness probe returns unhealthy
- Test graceful shutdown: send SIGTERM and assert in-flight requests complete before the process exits
- Assert startup failure behavior: misconfigure a required dependency and verify the service exits with a non-zero code and descriptive error

### Integration Tests

- Deploy the service in a real orchestrator and verify it receives no traffic until readiness is signaled
- Test shutdown drain: send requests during SIGTERM and verify all in-flight requests receive responses before the pod terminates
- Verify liveness vs readiness distinction: a temporarily unhealthy service should fail readiness but not liveness (no unnecessary restarts)

### Failure Injection

- Kill a critical dependency after startup and verify the readiness probe transitions to unhealthy, stopping new traffic
- Send SIGTERM during a long-running request and verify the service waits up to terminationGracePeriodSeconds before force-killing
- Simulate a health check endpoint that hangs and verify the orchestrator treats it as a timeout failure, not a success
