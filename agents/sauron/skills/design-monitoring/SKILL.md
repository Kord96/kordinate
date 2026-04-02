---
name: design-monitoring
description: >
  Design a monitoring system for a project — metrics to emit, log events to structure,
  health checks to add, dashboard specs, and alert rules. Depends on augur's atlas for
  architecture and charon's infrastructure context.
argument-hint: "<project> [--scope full|metrics|alerts|dashboards]"
---

Design a monitoring system for a project from scratch. Uses augur's atlas to understand the architecture and charon's infrastructure to understand the deployment.

## Arguments

`$ARGUMENTS` — Required: `<project>`. Optional:
- `--scope full|metrics|alerts|dashboards` — focus on a specific area (default: full)

## Dependencies

This skill depends on two other agents:

1. **Augur** — for architectural context:
   ```
   /kord augur analyze --detect-only <project>
   ```
   Atlas provides: components, flows, failure modes, external dependencies, detected patterns.

2. **Charon** — for infrastructure context:
   ```
   /kord alfred get config <cluster>
   ```
   Config provides: what's deployed where, what namespace, what services are exposed.

If the atlas doesn't exist, ask the user to run `/analyze` first.

## Procedure

1. **Load context** — read atlas.json for architecture. Read cluster config for infrastructure. Load the existing observability catalog if one exists (from a previous `/monitor` scan).

2. **Identify monitoring targets** — from the atlas, extract everything that needs monitoring:
   - Each component → needs metrics (request rate, error rate, latency)
   - Each external dependency → needs availability check and latency tracking
   - Each data flow → needs end-to-end latency and success rate
   - Each failure mode → needs detection signals and alerting
   - Each state store → needs capacity, connection pool, and query performance

3. **Design metrics** — for each target, specify:
   - Metric name (follow Prometheus naming conventions)
   - Type (counter, gauge, histogram, summary)
   - Labels (component, endpoint, status_code, etc.)
   - Where to emit (which source file, which function)
   - Implementation: library-specific code snippet (e.g., `prometheus_client` for Python, `prometheus/client_golang` for Go)

4. **Design log events** — for each component:
   - Structured log events for key operations (request start/end, error, state change)
   - Log levels (error for failures, warn for degradation, info for operations)
   - Required fields (correlation_id, component, operation, duration_ms)

5. **Design health checks** — for each component:
   - Readiness check (can it serve traffic?)
   - Liveness check (is it running?)
   - Dependency health (are its external deps reachable?)

6. **Design dashboards** — per component group (matching atlas groups):
   - Overview dashboard (RED metrics: rate, errors, duration)
   - Component detail dashboards (per-component deep dive)
   - Flow dashboards (end-to-end latency per data flow)
   - Grafana JSON spec or description

7. **Design alert rules** — for each failure mode in the atlas:
   - Alert condition (which metric, what threshold)
   - Severity (matches atlas failure mode severity)
   - Runbook reference (links to failure mode's recovery steps)
   - Routing (PagerDuty for critical, Slack for warning)

8. **Produce monitoring spec** — write to `$MEM/monitoring-spec.yaml`:
   - metrics (by component)
   - log_events (by component)
   - health_checks (by component)
   - dashboards (by group)
   - alerts (by failure mode)
   - implementation_plan (ordered list of changes to make)

## Report

```
## Monitoring Design: <project>

**Architecture**: N components, N external deps, N failure modes
**Metrics designed**: N (N counters, N gauges, N histograms)
**Log events**: N structured events across N components
**Health checks**: N readiness, N liveness, N dependency
**Dashboards**: N (N overview, N detail, N flow)
**Alerts**: N (N critical, N high, N medium)

### Implementation plan
1. Add prometheus_client to dependencies
2. Instrument <component> with request metrics (src/api/routes.py)
3. Add structured logging to <component> (src/workers/processor.py)
4. Create health check endpoints (src/api/health.py)
5. Deploy Grafana dashboards
6. Configure alert rules

### Spec written to: <path>
```
