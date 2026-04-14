---
description: App Contract — requirements every deployed application must satisfy
---
# App Contract

Every deployed application must satisfy these requirements. For allowed app label values, see `profile/topology.yaml`. For full infrastructure details, see `infra-atlas.json` (`new_workload_contract` section).

## Labels

Required pod label:
- `app` -- project name that owns this workload

Optional pod labels:
- `component` -- individual service name (e.g., `classifier`, `kafka`)
- `tier` -- operational role (e.g., `ingest`, `process`, `store`)

The `pod` label is auto-injected by Alloy from Kubernetes metadata.

## Annotations

Required for pods exposing `/metrics`:
- `prometheus.io/scrape: "true"`
- `prometheus.io/port: "<port>"`

## Observability Contract

### Metrics

Expose `/metrics` in Prometheus format. Alloy discovers via pod annotations and scrapes automatically.

### Logging

Structured JSON to stdout. Required fields:

| Field | Purpose |
|-------|---------|
| `level` | debug, info, warn, error |
| `component` | which service/module emitted the log |
| `event` | what happened |
| `timestamp` | when it happened |

Alloy tails pod stdout and writes to Loki. Additional fields become Loki labels automatically.

### Health

`GET /health` serves as both readiness and liveness probe. Returns 200 when the process is alive and ready to serve. Startup grace period: 30s.

### Vitals

Standalone deployment (one per app, not a sidecar) that evaluates app health by querying Prometheus. Vitals produces tri-state health gauges (`0=FAIL, 1=WARNING, 2=OK`) on port 9131.

Required evaluations:
- **process** -- is the process alive and responsive?
- **deps** -- are dependencies (databases, queues, APIs) reachable?

Extend with additional sections as needed (e.g., `vitals_ingestion`, `vitals_storage`, `vitals_serving`).

**VitalsMissing meta-alert required**: every app must have an alert rule that fires when vitals metrics disappear:
```yaml
- alert: VitalsMissing
  expr: absent(vitals_process{app="<name>"})
  for: 5m
```

### Detection

Atlas `failure_modes` entries carry structured detection metadata:
- `signals` -- observable symptoms (metric behavior, log patterns, error types)
- `concern` -- abstract category (dependency-availability, data-integrity, throughput, latency, resource-exhaustion, state-consistency)
- `source_pattern` -- concept catalog entry the detection derives from

Sauron reads these from the atlas and maps them to vitals evaluations and alert rules. The detection structure is portable -- augur defines what to watch, sauron implements how.

## Ownership Model

| Agent | Role |
|-------|------|
| **Augur** | Defines the contract (this file) and produces atlas with failure_modes/detection |
| **Charon** | Enforces on deployment (`/wrap` skill validates contract compliance) |
| **Sauron** | Implements monitoring (reads atlas, configures vitals + dashboards) |
| **Alfred** | Manages secrets and overlays (never hardcoded in manifests) |

## Dev Deployment Model

- **git-sync sidecar** pulls main every 3s
- **File watcher** for hot reload (nodemon/uvicorn depending on runtime)
- **Image rebuilds only on dependency changes** (package.json, requirements.txt, etc.)
- **Webhook receiver** gates the deployment pipeline

## Enforcement

Charon's `/wrap` skill validates the contract on deployment:
- `app` label must be present with an allowed value from `profile/topology.yaml`
- `/metrics` endpoint must return valid Prometheus format
- Log output must be structured JSON with required fields
- Health endpoint must respond at `GET /health`

Apps that do not satisfy the contract are rejected.
