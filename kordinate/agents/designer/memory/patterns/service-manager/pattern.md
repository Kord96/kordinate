---
description: Service Manager architectural pattern
curated: true
scope: global
preloaded: none
---
# Service Manager

## Recognition

How to identify this pattern in code.

### Signatures

- Signal handlers registering for graceful shutdown (`signal.signal(signal.SIGTERM, handler)`)
- Health endpoints exposed at `/healthz` and `/readyz` paths
- `livenessProbe` and `readinessProbe` configuration in Kubernetes pod specs
- `ServiceManager` class coordinating startup, readiness, and shutdown phases
- `orchestrator` imports or orchestration-layer integration for lifecycle reporting
- Process lifecycle management with explicit state transitions (starting, ready, draining, stopped)
- Graceful shutdown logic draining in-flight requests and flushing buffers before exit
- `terminationGracePeriodSeconds` configuration in pod specs

### Confidence

- **high** -- `ServiceManager` class with SIGTERM signal handlers, `/healthz`+`/readyz` endpoints, and `livenessProbe`/`readinessProbe` in K8s specs
- **medium** -- Signal handlers with graceful shutdown drain logic and health endpoints, but without a dedicated manager class
- **low** -- Health check endpoints or liveness probes present without explicit shutdown handling or lifecycle state management

## Architecture

Look for clean lifecycle phases: startup completes before serving, shutdown drains before closing.

### Review Checklist

- Startup validates config and dependencies before marking ready
- Health checks run periodically and report to orchestrator (liveness + readiness)
- Shutdown handles SIGTERM gracefully — drains in-flight requests, flushes buffers
- Startup failures produce clear error messages and exit with non-zero code
- No traffic served until readiness is explicitly signaled

### Anti-patterns

- Serving traffic before dependencies are connected (premature readiness)
- Shutdown kills in-flight requests without draining (data loss)
- Health check always returns healthy regardless of actual state
- No distinction between liveness and readiness probes

## Monitoring

Track service lifecycle transitions and health check outcomes to detect unstable services before they impact availability.

### Key Metrics

- `service_state` (gauge) — current lifecycle state per service (0=stopped, 1=starting, 2=ready, 3=draining)
- `service_restarts_total` (counter) — restart count per service (including crash restarts)
- `health_check_duration_seconds` (histogram) — health check execution time per service
- `health_check_failures_total` (counter) — failed health checks per service and probe type (liveness/readiness)

### Alerts

- Service restart count exceeding threshold in a rolling window (crash loop)
- Health check failing consecutively beyond configured threshold
- Service stuck in starting state beyond expected startup time
- Readiness probe failing while liveness passes (service alive but not serving)

## Deployment

Graceful shutdown, health check timing, and startup dependencies determine whether rollouts cause traffic drops.

### Rollout Implications

- New pods must pass readiness probes before old pods begin terminating — configure minReadySeconds to avoid premature traffic shifting
- Startup dependencies (database, cache, message broker) must be reachable before readiness is signaled — use init containers or startup probes
- SIGTERM handling must drain in-flight requests and flush buffers within terminationGracePeriodSeconds or data is lost
- Health check timing mismatches between the orchestrator and the service can cause premature removal from load balancing

### Pre-deploy Checklist

- Verify terminationGracePeriodSeconds exceeds the maximum expected request drain time
- Confirm readiness and liveness probe intervals are tuned to avoid false positives during startup
- Check that all startup dependencies are available in the target environment before beginning rollout

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
