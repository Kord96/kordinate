---
description: Two-layer monitoring model — Alloy collects, Vitals evaluates
curated: true
scope: global
---
# Monitoring

Two layers: Alloy collects per-pod data, Vitals evaluates per-app health.

## The `app` Label

Every pod must have the Kubernetes label `app: <name>`. Alloy copies it to every metric and log it collects, making all data queryable by application across Prometheus, Loki, and Grafana.

## Alloy: Pod-Level Collection

Alloy runs in the monitor namespace and collects three concerns per pod:

| Concern | Source | How |
|---------|--------|-----|
| Infra metrics | kubelet, cAdvisor | CPU, memory, network, disk — automatic for all pods |
| App metrics | pod `/metrics` | Scraped if pod has `prometheus.io/scrape` annotation |
| Logs | pod stdout | Tailed via K8s API, written to Loki |

Infra metrics are always available — no app instrumentation needed. App metrics are opt-in. Not every pod needs `/metrics`.

### Pod Annotations

For pods that expose `/metrics`:

```yaml
metadata:
  labels:
    app: my-app
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "<port>"
```

Pods without `/metrics` still get infra metrics and log collection — only the `app` label is required.

### Logs

Apps write structured JSON to stdout. Alloy tails pod stdout and writes to Loki. Log delivery is best-effort.

Required fields: `level` (info/warning/error), `event` (what happened). Additional fields become Loki labels automatically.

## Vitals: App-Level Evaluation

Each app deploys one vitals pod in its own namespace that evaluates health by querying Prometheus and Loki. Vitals is standalone (not a sidecar) because it needs a cross-pod view.

Vitals produces two types of metrics:

1. **Health gauges** — tri-state (`0=FAIL, 1=WARNING, 2=OK`) evaluations of app concerns
2. **Derived metrics** — app-level aggregations that don't exist at the pod level

Alloy scrapes vitals like any other pod.

### Health Gauges

| Metric | What it answers |
|--------|----------------|
| `vitals_process{process}` | Is this process alive? |
| `vitals_<section>{check}` | Is this concern healthy? |

Recommended sections (extend as needed): `vitals_deps`, `vitals_ingestion`, `vitals_storage`, `vitals_serving`, `vitals_queue`.

### Derived Metrics

App-level aggregations computed from pod-level data. Examples: `vitals_pipeline_latency_seconds`, `vitals_consumer_lag_total`, `vitals_throughput_messages_per_second`.

### Deployment

One vitals deployment per app, per namespace. Requires both `PROMETHEUS_URL` and `LOKI_URL` env vars. Port 9131, with `prometheus.io/scrape` annotation so Alloy collects vitals metrics.

## Dashboards

Dashboards are stored as JSON and provisioned via ConfigMaps:

```bash
kubectl create configmap grafana-dashboards -n monitor \
  --from-file=dashboards/ --dry-run=client -o yaml | kubectl apply --server-side -f -
```

Grafana polls for changes every 30 seconds.

## Alerting

### Meta-alerts

Detect silent vitals failures — if vitals goes down, health visibility is lost:

```yaml
- alert: VitalsMissing
  expr: absent(vitals_process{app="my-app"})
  for: 5m
```

### App alerts

Alert rules are defined per-app based on vitals gauges (e.g., `vitals_deps == 0` for critical, `vitals_ingestion == 1` for warning).

## Onboarding a New App

1. Add the `app` label to all pods
2. Optionally expose `/metrics` with `prometheus.io/scrape` annotation
3. Deploy a vitals pod that evaluates health and derived metrics
4. Add a Grafana dashboard
5. Add alert rules for critical vitals gauges

Vitals is not required for short-lived jobs or CronJobs. Platform infrastructure has its own health mechanisms and does not use vitals.
