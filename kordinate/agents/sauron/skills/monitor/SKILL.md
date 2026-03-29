---
name: monitor
description: >
  Scan a project for observability signals, identify monitoring gaps, and diagnose live issues.
  Combines static codebase scanning with live system debugging. Depends on augur's atlas
  for architectural context.
argument-hint: "<project> [--diagnose <symptom>] [--scan-only]"
scope: global
---

Scan a project for observability signals and diagnose issues. Uses augur's atlas to understand what components exist and what should be monitored.

## Arguments

`$ARGUMENTS` — Required: `<project>`. Optional:
- `--diagnose <symptom>` — switch to diagnosis mode: trace a live issue using the observability catalog
- `--scan-only` — produce the catalog only, skip gap analysis

## Dependencies

This skill depends on augur's analysis for architectural context:

```
/kord augur analyze --detect-only <project>
```

Read the atlas from `<project>/.kord/agents/augur/memory/atlas.json`. The atlas provides: components (what to monitor), flows (what paths to trace), failure modes (what breaks), external dependencies (what to watch).

If the atlas doesn't exist, ask the user to run `/analyze` first.

## Procedure

### Phase 1 — Scan

1. **Load atlas** — read atlas.json. Build a list of components, external dependencies, and failure modes. Each is a monitoring target.

2. **Scan observability signals** — for each source file in the project, find:
   - **Metrics**: Prometheus counters/gauges/histograms/summaries, StatsD calls, custom metric emissions
   - **Log events**: structured log calls with levels, log patterns (what gets logged at error/warn/info)
   - **Health checks**: `/health`, `/ready`, `/live` endpoints, health check functions
   - **Tracing**: OpenTelemetry spans, distributed tracing instrumentation
   - **Alerting**: alert rule definitions, PagerDuty/Slack integrations

3. **Map signals to components** — using the atlas, map each discovered signal to the component it belongs to. A metric in `src/api/routes.py` maps to the `api` component.

4. **Identify gaps** — for each atlas component and external dependency:
   - Has metrics? If not → gap
   - Has health check? If not → gap
   - Has error logging? If not → gap
   - Has failure detection? (from atlas failure modes) If detection is `["none"]` → critical gap
   - Has recovery mechanism? If recovery is `["none"]` → gap

5. **Produce catalog** — write `<project>/.kord/agents/sauron/memory/observability-catalog.yaml` with: signals by component, gaps by severity, coverage percentage.

### Phase 2 — Diagnose (only with `--diagnose`)

6. **Load catalog** — read the observability catalog (from phase 1 or a previous scan).

7. **Trace the symptom** — starting from the reported symptom:
   - Which component is affected? (match against atlas components)
   - What signals does that component have? (from catalog)
   - What flows pass through it? (from atlas data_flows)
   - What failure modes affect it? (from atlas failure_modes)

8. **Check live signals** — if cluster access is available:
   - Query Prometheus/Grafana for the component's metrics
   - Check recent logs via Loki for error patterns
   - Check health endpoints

9. **Propose root cause** — trace the failure cascade using atlas failure modes. Identify: trigger, cascade path, detection signals that fired (or should have), recovery steps.

10. **Report** — structured diagnosis: symptom → affected component → signals checked → likely root cause → recommended fix.

## Report (scan mode)

```
## Observability: <project>

**Components scanned**: N
**Signals found**: N metrics, N log events, N health checks, N traces
**Coverage**: X% of components have metrics, Y% have health checks
**Gaps**: N critical, N recommended

### Critical gaps
| Component | Missing | Impact |
|-----------|---------|--------|
| ...       | ...     | ...    |

### Catalog written to: <path>
```
