---
description: Health Check architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [lifecycle, observability]
---
# Health Check

## Recognition

How to identify this pattern in code.

### Signatures

- Endpoints: `/health`, `/healthz`, `/ready`, `/readyz`, `/live`, `/livez`, `/status`
- K8s probe definitions: `livenessProbe`, `readinessProbe`, `startupProbe` in pod specs
- Dependency health aggregation (checking database, cache, message queue connectivity)
- Health status enum or response: `UP`, `DOWN`, `DEGRADED`, `STARTING`
- Spring Boot Actuator `/actuator/health` with auto-configured health indicators
- Health check libraries or frameworks with pluggable health indicator registration

### Confidence

- **high** -- separate liveness and readiness endpoints with dependency checks, K8s probes configured, health status aggregation
- **medium** -- single `/health` endpoint returning 200 OK without checking dependencies
- **low** -- root endpoint (`/`) returning a response used informally as a health signal

## Architecture

Look for separate liveness and readiness probes with appropriate dependency health checks at each level.

### Review Checklist

- Liveness probe checks only process health (is the application alive), not dependency health
- Readiness probe checks dependency connectivity (can the application serve traffic)
- Startup probe is used for slow-starting applications to prevent premature liveness failures
- Probe timeouts and intervals are tuned to avoid false positives (not too aggressive)
- Health endpoints are not exposed publicly or are protected from abuse
- Dependency checks have their own timeouts (a slow database check does not hang the health endpoint)

### Anti-patterns

- Liveness probe checking external dependencies (database down kills healthy pods, cascading failure)
- Health endpoint that performs expensive operations (heavy queries, full connection tests on every call)
- No readiness probe (traffic routed to pods before they can handle requests)
- Same endpoint and logic for both liveness and readiness (they serve different purposes)
