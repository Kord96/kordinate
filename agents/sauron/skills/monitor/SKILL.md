---
name: monitor
description: >
  Monitor a running system — read metrics, logs, dashboards, and health checks.
  Detect anomalies, diagnose issues, trace failures. Depends on augur's atlas for
  architecture context and charon's config for cluster access.
argument-hint: "<project> [--diagnose <symptom>] [--check] [--scan-code]"
---

Monitor a running system. Reads Prometheus metrics, Loki logs, Grafana dashboards, and health endpoints. Uses augur's atlas to understand which components to watch and charon's config for cluster access.

## Arguments

`$ARGUMENTS` — Required: `<project>`. Optional:
- `--diagnose <symptom>` — trace a specific issue: "API returning 503s", "queue backing up", "high latency on /checkout"
- `--check` — quick health check: hit all health endpoints, check key metrics for anomalies
- `--scan-code` — also scan the codebase for observability signals (static analysis, slower)

Default (no flags): full monitoring review — read all available signals, report status and anomalies.

## Dependencies

1. **Augur** — architectural context:
   Read atlas from `/kord/agents/augur/memory/projects/<project>/atlas.json` (augur's project memory). Provides: components (what to check), flows (what paths to trace), failure modes (what cascades to look for), external dependencies (what external health to verify).

2. **Augur monitoring-spec** (optional, enriches monitoring):
   If available, read augur's monitoring-spec.yaml to know exactly which metrics the project should emit. Resolution order:
   - Artifact path from prompt: `[Artifacts] monitoring-spec: <path>`
   - Augur project memory: `/kord/agents/augur/memory/projects/<project>/monitoring-spec.yaml`
   When the spec is available, use it to validate that all designed metrics are actually emitting (cross-reference with live scrape). Without the spec, fall back to convention-based checks.

3. **Charon/Alfred** — cluster access:
   ```
   /kord alfred get config <cluster>
   ```
   Provides: Tailscale IPs, namespaces, service ports, kubeconfig context.

4. **Sauron implementation status** (optional):
   If `/design-monitoring` has been run, check `$MEM/implementation-status.yaml` for known metric validation results and deployed dashboards/alerts.

If atlas doesn't exist, ask user to run `/analyze` first. If cluster config is unavailable, report what can be checked without live access.

## Procedure

### Step 1 — Load context

Read atlas.json for component inventory. Get cluster config for access details.

If augur's monitoring-spec.yaml is available (artifact path or augur project memory), load it to get the designed metric names, alert conditions, and dashboard definitions. This enables precise validation: check whether the service emits exactly the metrics the spec expects, rather than relying only on convention.

If sauron's `$MEM/implementation-status.yaml` exists (from a prior `/design-monitoring` run), load it for baseline comparison.

Build a monitoring checklist: each component x signal types (metrics, logs, health, traces). When a monitoring spec is available, augment the checklist with the specific metric names and types from the spec.

### Step 2 — Check health endpoints

For each component with a known health endpoint (from atlas or convention):
```bash
curl -s http://<tailscale-ip>:<port>/health
curl -s http://<tailscale-ip>:<port>/ready
```
Record: status, response time, any error details.

### Step 3 — Read Prometheus metrics

Query Prometheus for each component's key signals:
- **Request rate**: `rate(http_requests_total{app="<component>"}[5m])`
- **Error rate**: `rate(http_requests_total{app="<component>",status=~"5.."}[5m])`
- **Latency**: `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{app="<component>"}[5m]))`
- **Saturation**: CPU, memory, connection pool utilization

Use Grafana MCP tools if available, or direct PromQL via API.

**Spec cross-reference** (when monitoring-spec.yaml is available):
For each metric in the spec, query Prometheus to verify it exists and is being scraped. Classify each as:
- `EMITTING` — metric present in Prometheus with expected type
- `MISSING` — metric not found (not instrumented or not scraped)
- `TYPE_MISMATCH` — metric exists but type differs from spec
- `LABELS_MISSING` — metric exists but expected labels are absent

This produces a spec coverage score: `emitting / total_spec_metrics`.

### Step 4 — Read recent logs

Query Loki for each component's recent error and warning logs:
```
{app="<component>"} |= "error" or |= "ERROR" | logfmt
```
Look for: error spikes, repeated patterns, new error types, correlation with metric changes.

### Step 5 — Check external dependencies

For each external dependency in the atlas:
- Is it reachable? (health check or ping)
- What's the current latency? (from metrics)
- Is the circuit breaker open? (from metrics or logs)
- Any resilience patterns firing? (retries, fallbacks)

### Step 6 — Diagnose (with `--diagnose`)

Starting from the reported symptom:
1. **Identify affected component** — match symptom to atlas component
2. **Check its signals** — metrics (is error rate up?), logs (what errors?), health (is it responding?)
3. **Trace the flow** — follow the atlas data_flow that the symptom relates to. Check each component in the flow path.
4. **Check cascade** — match against atlas failure_modes. Is this a known failure pattern? What's the expected cascade?
5. **Propose root cause** — based on signal evidence: which component broke first, what cascaded, what's the fix.

### Step 7 — Scan code (with `--scan-code`)

Static analysis of the codebase for observability signals:
- Grep for metric definitions (Counter, Gauge, Histogram)
- Grep for structured log calls
- Find health check endpoints
- Find tracing spans
- Map each signal to its atlas component
- Identify gaps (components with no signals)

Write catalog to `$MEM/observability-catalog.yaml`.

### Step 8 — Report

```
## Monitor: <project> (<timestamp>)

### Health
| Component | Status | Response | Latency |
|-----------|--------|----------|---------|

### Metrics (last 5m)
| Component | Request Rate | Error Rate | p99 Latency |
|-----------|-------------|------------|-------------|

### Spec Coverage (if monitoring-spec.yaml available)
**Source**: <path to monitoring-spec.yaml>
| Metric | Type | Status |
|--------|------|--------|
| <metric_name> | counter | EMITTING / MISSING / TYPE_MISMATCH |

**Coverage**: N/N metrics emitting (N%)
**Missing**: <list of metrics not yet instrumented>

### External Dependencies
| Dependency | Reachable | Latency | Circuit Breaker |
|-----------|-----------|---------|-----------------|

### Anomalies
- <component>: error rate 5x above baseline
- <dependency>: latency spike to 2s (normally 50ms)

### Log Events (errors, last 1h)
| Component | Count | Pattern |
|-----------|-------|---------|

### Diagnosis (if --diagnose)
**Symptom**: <reported symptom>
**Root cause**: <component> — <what happened>
**Evidence**: <metrics/logs that support this>
**Cascade**: <what else was affected>
**Fix**: <recommended action>
```
