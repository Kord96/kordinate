# Observability Contract

How apps expose telemetry to the platform. Three concerns — logs, metrics, health — with clear ownership boundaries. All pods belonging to an app share the `app` label — this is how Gateway Alloy, Vitals, and Grafana identify which metrics and logs belong together.

## Overview

```mermaid
flowchart TB
    subgraph app["app: my-app"]
        P1[pod 1 — /metrics]
        P2[pod 2 — /metrics]
        PN[pod N — /metrics]
        VIT[Vitals — /metrics :9131]
        P1 ~~~ P2 ~~~ PN ~~~ VIT
    end

    P1 & P2 & PN -->|/metrics| AL
    VIT -->|health metrics| AL
    PR -.->|app metrics query| VIT

    subgraph mon[monitor namespace]
        AL[Alloy] --> PR[Prom]
    end
```

!!! tip ""
    All pods — including vitals — share the `app` label. Alloy uses this label to group metrics and logs by application.

### Log shipping

```mermaid
flowchart LR
    subgraph app["app: my-app"]
        P[pods — stdout JSON]
    end

    P -->|stdout| K8S[K8s API]
    K8S -->|tail| AL[Alloy] --> LK[Loki]
```

Apps write structured JSON to stdout. Alloy tails pod logs via the K8s API — apps don't push to Loki directly. Log delivery is best-effort.

| Concern | Owner | Interface | Consumer |
|---------|-------|-----------|----------|
| **Logs** | app pods | structured JSON → stdout | Gateway Alloy (tails via K8s API) |
| **Metrics** | app pods | `/metrics` on app port | Gateway Alloy (scrapes) |
| **Health** | vitals pod | `/metrics` on `:9131` | Gateway Alloy (scrapes) |

## Logs

Apps write structured JSON to stdout. No special libraries required — any logger that outputs JSON works.

Gateway Alloy tails pod stdout via the K8s API and writes to Loki. Log delivery is **best-effort** — apps must not block on stdout. Kubernetes buffers stdout in container runtime log files, which rotate.

Required fields:

| Field | Purpose |
|-------|---------|
| `level` | Log level (info, warning, error) |
| `event` | What happened |

Additional fields are app-defined and become Loki labels automatically via the Alloy processing pipeline.

## Metrics

Apps expose `/metrics` in Prometheus format on their process port. Gateway Alloy discovers and scrapes via pod annotations.

Required pod annotations:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "<app-metrics-port>"
```

Gateway Alloy normalizes metrics — drops raw `kube_*`/`kafka_*` prefixes, keeps app-specific metrics. Apps should use descriptive metric names with an app-specific prefix.

## Health (Vitals)

Each app deploys **one vitals pod per namespace** that evaluates the app's health and produces standardized health gauges.

### How it works

1. Vitals queries **Gateway Prom** for app metrics (cross-namespace: `prometheus.monitor.svc.cluster.local:9090`) — raw metrics, aggregations, liveness (`up{}`)
2. Evaluates thresholds and health logic (app-specific domain knowledge)
3. Exposes `vitals_*` gauges on `:9131/metrics`
4. Gateway Alloy scrapes vitals like any other pod

### Why standalone, not sidecar

Health evaluation is often **cross-cutting** — checking Kafka lag across consumer groups, aggregating storage usage across volumes, evaluating pipeline throughput. These require a system-wide view that a per-pod sidecar can't provide. One vitals pod per app keeps the deployment simple and gives the evaluator access to all of the app's metrics in Prom.

### Metric convention

All gauges use **0 = FAIL, 1 = WARNING, 2 = OK**.

| Metric | What it answers |
|--------|----------------|
| `vitals_process{process}` | Is this process alive? |
| `vitals_<section>{check}` | Is this concern healthy? |

**Recommended sections** — use these when the concern fits, extend with app-specific sections as needed:

| Section | What it covers |
|---------|---------------|
| `vitals_deps` | External dependencies (databases, APIs, caches) |
| `vitals_ingestion` | Data intake pipelines (Kafka lag, consumption rates) |
| `vitals_storage` | Persistence layer (PVC usage, DB file sizes) |
| `vitals_serving` | Request handling, API readiness |
| `vitals_queue` | Message queue consumers/producers |

Check labels should be short, specific, snake_case: `vitals_deps{check="postgres_primary"}`, not `vitals_deps{check="pg"}`.

### Deployment

One vitals deployment per app, per namespace:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vitals
  labels:
    app: my-app
    component: vitals
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: my-app
        component: vitals
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9131"
    spec:
      containers:
        - name: vitals
          args: ["-m", "monitor.vitals", "--port", "9131"]
          env:
            - name: PROMETHEUS_URL
              value: "http://prometheus.monitor.svc.cluster.local:9090"
          ports:
            - containerPort: 9131
              name: metrics
```

### Meta-alerting

The platform should detect silent vitals failures:

```yaml
- alert: VitalsMissing
  expr: absent(vitals_process{app="my-app"})
  for: 5m
  labels:
    severity: warning
```

## When to use

- Every app deployed to the cluster
- Any service that needs health visibility in Grafana
- Apps with multiple processes that need cross-component health evaluation

## When not to use

- Short-lived jobs or CronJobs — use exit codes and job status metrics instead
- Platform infrastructure (Alloy, Prom, Loki) — these have their own health mechanisms

## Related patterns

- [Service Manager](service-manager.md) — managed processes should comply with this contract
