# Infrastructure Monitoring Data Flow

> **For your specific cluster topology and federation jobs, see `profile/topology.yaml`.**

## Architecture

Each k3s cluster is standalone with its own observability stack. The master namespace provides a unified cross-cluster view by pulling from all clusters via Tailscale — clusters are unaware of master.

### Per-Cluster Gateway (monitor namespace)
- **Gateway Alloy**: Scrapes all pods (via prometheus.io annotations), kubelet/cAdvisor, kube-state-metrics, Kafka JMX, node-exporter. Injects `cluster` label. Writes to local Prometheus via remote_write. Tails pod logs and pushes to local Loki.
- **Gateway Prometheus**: Short-term buffer (retention per `profile/topology.yaml`).
- **Gateway Loki**: Log storage with rate limiting.
- **Gateway (Tailscale sidecar)**: Exposes Prom, Loki, and K8s API over Tailscale.

The `master` namespace (one cluster only) provides a unified cross-cluster view:

- **Master Prometheus** — FEDERATES from all gateway Prometheus instances. It does NOT directly scrape pods. This is the single datasource for Grafana.
- **Master Alloy** — handles ONLY logs (tails pods via K8s API, writes to Master Loki). No metrics scraping.
- **Master Loki** — receives logs from Master Alloy.
- **Grafana** — queries only master's local Prometheus and Loki.

## Data Flow

```
Each remote cluster:
  pods/nodes → Gateway Alloy (scrape) → Gateway Prometheus (buffer)
                                              ↓ federate
                                     Master Prometheus (unified view)

Logs:
  pods → Master Alloy (K8s API tail) → Master Loki
```

## Cluster Label

The `cluster` label is injected by each gateway Alloy via the `CLUSTER_NAME` environment variable, sourced from a `cluster-identity` ConfigMap that the deployer sets per cluster (actual cluster names are defined in `profile/topology.yaml`).

## Metrics Flow

```
Pod metrics → Gateway Alloy scrapes → Gateway Prom (3h) → Master Alloy federates → Master Prom (30d) → Grafana
Pod logs    → Gateway Alloy tails   → Gateway Loki (30d) → Master Alloy tails     → Master Loki (30d) → Grafana
```

## Available Metrics Catalog

### Application Metrics (via Gateway Alloy normalization)
- `pipeline_flush_*` — flush operations (count, duration, errors)
- `pipeline_entities_*` — entity processing counts
- `pipeline_buffer_*` — buffer utilization metrics
- `pipeline_consume_*` — Kafka consumption metrics

### Container Metrics (from kubelet/cAdvisor)
- `container_memory_working_set_bytes` — container memory usage
- `container_cpu_usage_seconds_total` — container CPU usage

### Kubernetes State Metrics (from KSM + kubelet)
- `kube_pod_container_status_restarts_total` — container restart counts
- `kubelet_volume_stats_*` — PVC usage statistics

### Kafka Metrics (from Kafka JMX)
- `pipeline_kafka_topic_size_bytes` — topic storage size (normalized from kafka_log_log_size)

### Normalized Metrics (Gateway Alloy relabeling)
- `pipeline_pvc_used_bytes`, `pipeline_pvc_capacity_bytes` — normalized from kubelet_volume_stats_*
- `pipeline_container_restarts_total` — normalized from kube_pod_container_status_restarts_total
- `pipeline_cronjob_suspended`, `pipeline_cronjob_next_schedule_time` — normalized from kube_*
- `pipeline_kafka_topic_size_bytes` — normalized from kafka_log_log_size

### Host Metrics (from node-exporter)
- `node_cpu_seconds_total`, `node_memory_MemTotal_bytes`, `node_memory_MemAvailable_bytes`
- `node_filesystem_*`, `node_disk_*`, `node_network_*`

## Sentinel (Alert Evaluation)

### Overview
- Runs in the prod namespace
- Queries Prometheus via the gateway service
- Deployment manifest located in the project's deploy directory

### 12 Evaluation Sections
1. **Process status** — are all expected pods running?
2. **Ingestion** — Kafka consumption rates, lag
3. **Buffers** — pipeline buffer utilization
4. **Enrichment** — enrichment pipeline health
5. **Downloads** — download job status
6. **Derived** — derived data computation health
7. **Storage** — DuckDB and PVC usage
8. **Dependencies** — Kafka, Postgres, Redis health
9. **Clock skew** — node time synchronization
10. **FD exhaustion** — file descriptor limits
11. **DB sizes** — database file sizes
12. **Composites** — compound health checks combining multiple signals

## Known Monitoring Gaps

Check `profile/projects/` for project-specific monitoring gaps.

## Rules

- **Never remove federation jobs** (listed in `profile/topology.yaml` under `monitoring.federation`) from Master Prometheus — this is the only path for metrics to reach the unified view.
- **Never add direct pod/node scraping to Master Alloy** — gateways already collect everything. Adding direct scrapes creates duplicate ingestion with conflicting labels.
- **Master Alloy is logs-only** — if you need to change metrics collection, modify the gateway Alloy config, not master.
- When in doubt about data flow, consult deployer: `/consult deployer "explain the monitoring data flow for <component>"`.
