---
kind: concept
name: health-check
signatures:
  concept: health-check
  positive:
    strong:
    - dedicated health or readiness endpoints
    - explicit K8s probe configuration
    medium:
    - single health endpoint with lightweight checks
    weak:
    - root endpoint used informally as health
  negative:
  - liveness depends on external dependencies
  - health endpoint performs expensive operations
  notes:
  - Favor evidence that distinguishes liveness from readiness.
type: pattern
abstraction:
- lifecycle
- observability
scope: cross-cutting
status: primary
review_questions:
  threshold: 5
  entries:
  - id: health-check-dedicated-endpoint
    prompt: Is there a dedicated health, liveness, or readiness endpoint or probe?
    weight: 3
    signals:
    - /health
    - /ready
    - livenessProbe
  - id: health-check-correct-scope
    prompt: Are liveness and readiness concerns kept distinct enough to avoid cascading
      restarts?
    weight: 2
    signals:
    - readiness
    - liveness
monitoring:
  applies_to:
  - component
  - dependency
  health_signals:
  - name: readiness.failure.rate
    description: Frequency of failed readiness checks that would remove the instance
      from service.
  - name: liveness.failure.rate
    description: Frequency of failed liveness checks that would trigger restart behavior.
  - name: health_check.latency
    description: Time taken to execute health probes, especially if they touch dependencies.
  business_metrics: []
  gaps:
  - Combining dependency health into liveness without visibility can trigger cascading
    restart loops.
family: design-patterns
---

# Explanation

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

### Relationship To Other Concepts

- Related to [graceful-degradation](/concepts/graceful-degradation) because health signals often determine whether a system should keep serving in degraded mode or be removed from traffic.
- Related to [canary](/concepts/canary) because canary rollout controllers depend on clear health signals to promote or roll back.
- Related to [leader-election](/concepts/leader-election) when readiness or liveness depends on current leadership or election state.

### Boundary

Use `health-check` when a service explicitly exposes machine-readable signals about liveness, readiness, or dependency health for orchestration or monitoring.

Do not use it for ordinary status pages or logs. The defining property is an operational probe surface intended for automated systems.
