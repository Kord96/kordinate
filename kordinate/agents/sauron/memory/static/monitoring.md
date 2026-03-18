# Monitoring Layers

Monitoring has four layers. Sauron handles all four, but with different approaches per layer.

## 1. Physical Resources

Always monitor. Node metrics come from Alloy's built-in `node_exporter` integration (no standalone DaemonSet). Container metrics come from cAdvisor via kubelet. Sauron doesn't generate these — just ensures they're collected and scraped.

Metrics: CPU usage, memory (total/available/swap), disk (usage/IO), network (bytes sent/recv), container resources.

## 2. Health Status

Discoverable from the project's dependencies and processes. Sauron generates these by auditing the codebase.

**Per-process:** Is it running? Is it stuck? (check port reachability, recent activity)
**Per-dependency:** Is Kafka/Postgres/Redis reachable? (TCP checks, ping)
**Composite:** Roll up process + dependency health into section-level status gauges (0=fail, 1=warning, 2=ok)

Pattern: a health daemon that periodically checks all processes and dependencies, exposes `service_status{process}` and `section_status{section}` gauges.

## 3. Design-Pattern Metrics

Determined by which framework the project uses. Sauron generates these from the Design Patterns table in CLAUDE.md.

### Stoik
Consumer loop metrics: `messages_consumed_total`, `messages_flushed_total`, `buffer_size`, `flush_duration_seconds`, `parse_errors_total`, `consumer_lag`

### Orchestrator
Lifecycle metrics: `service_status`, `service_healthy`, `batch_completed_total`, `batch_last_duration_seconds`, `task_success`/`task_failed`, `batch_cpu_percent`, `batch_memory_bytes`

## 4. Project-Specific

Only the developer knows these. Sauron should **ask** what business metrics matter, then implement them.

Examples: spam/clean message rates, entity counts by type, enrichment coverage, classification scores, job success timestamps.

## Reference Patterns

- `metrics_pusher.py` — How to expose Prometheus metrics in k8s (prometheus_client + pod annotations)
- `grafana_api.py` — Programmatic dashboard push/pull via Grafana HTTP API

## Health Logs

Complement metrics with structured warning/error logs. Rate-limit to avoid storms.

| Category | Warning | Error |
|----------|---------|-------|
| **Performance** | Slow operations (>threshold) | Timeouts, deadlocks |
| **Throughput** | Low consume/flush rate | Zero throughput |
| **Resources** | High memory/disk usage | OOM, disk full |
| **Dependencies** | Slow calls, retries | Connection failures |
| **Data Quality** | High error ratio | Data corruption |
| **Backpressure** | Growing backlog/lag | Backlog exceeding capacity |

## Grafana Dashboard Provisioning

Dashboards are stored as JSON in `agents/deployer/manifests/master/base/dashboards/` and provisioned via ConfigMaps:

- `dashboards/cluster/` — per-cluster dashboards (loaded on all Grafana instances)
- `dashboards/master/` — master-only dashboards (loaded on home Grafana only)

To update dashboards after editing JSONs:
```
kubectl create configmap grafana-dashboards-cluster -n monitor --from-file=dashboards/cluster/ --dry-run=client -o yaml | kubectl apply --server-side -f -
```

Grafana polls for changes every 30 seconds.
