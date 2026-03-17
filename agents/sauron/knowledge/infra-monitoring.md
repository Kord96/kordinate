# Infrastructure Monitoring Data Flow

## Architecture

Each k3s cluster is standalone with its own observability stack. The master namespace provides a unified cross-cluster view by pulling from all clusters via Tailscale — clusters are unaware of master.

### Vandc Cluster (monitor namespace)
- **Gateway Alloy**: Scrapes all pods (graphdb-pods via prometheus.io annotations), kubelet/cAdvisor (container metrics), kube-state-metrics, Kafka JMX, node-exporter. Injects `cluster=vandc` label. Writes to local Prometheus via remote_write. Tails pod logs and pushes to local Loki.
- **Gateway Prometheus**: 3h retention, port 9090. Short-term buffer.
- **Gateway Loki**: 30d retention, port 3100. Rate limits: 16MB/s ingestion.
- **Gateway (Tailscale sidecar)**: Exposes Prom:9090, Loki:3100, K8s API:6443 over Tailscale at 100.107.8.117.

### Master Cluster (master namespace)
- **Master Alloy**: Pulls /federate from all cluster Proms via Tailscale (vandc @ 100.107.8.117:9090, home @ 100.113.48.89:9090). Tails logs from both clusters via remote kubeconfig over Tailscale. Writes to Master Prom and Master Loki.
- **Master Prometheus**: 30d retention, port 9191. Aggregated long-term storage.
- **Master Loki**: 30d retention, port 3100. Aggregated logs.
- **Grafana**: Reads from Master Prom and Loki. Dashboards provisioned via ConfigMaps.

## Cluster Label

The `cluster` label is injected by each gateway Alloy via the `CLUSTER_NAME` environment variable, sourced from a `cluster-identity` ConfigMap that the deployer sets per cluster (e.g., `vandc`, `home`).

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
- Runs in prod namespace on vandc cluster
- Queries Prometheus at `gateway.gateway.svc.cluster.local:9090` (cross-namespace via gateway Tailscale sidecar)
- Deployment manifest: `/home/claude/logbd/deploy/graphdb/monitoring/sentinel.yaml`

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

### CRITICAL: MinIO Not Monitored
- **What**: MinIO (prod namespace) is the snapshot backend (SNAPSHOT_BACKEND=minio), S3-compatible
- **Problem**: NOT scraped by Prometheus despite being a critical dependency after snapshot migration
- **Available but unused**: MinIO exposes metrics at `/minio/v2/metrics/cluster`
- **Impact**: No alerting on MinIO health, storage capacity, or API errors
- **Deployment**: `/home/claude/logbd/deploy/graphdb/storage/minio.yaml`

### Sentinel Does Not Check MinIO
- No MinIO evaluation section exists in Sentinel's 12 checks
- If MinIO goes down, snapshots fail silently — no alert fires

## Rules

- **Never remove federation jobs** (`federate-vandc`, `federate-home`) from Master Prometheus — this is the only path for metrics to reach the unified view.
- **Never add direct pod/node scraping to Master Alloy** — gateways already collect everything. Adding direct scrapes creates duplicate ingestion with conflicting labels.
- **Master Alloy is logs-only** — if you need to change metrics collection, modify the gateway Alloy config, not master.
- When in doubt about data flow, consult deployer: `/consult deployer "explain the monitoring data flow for <component>"`.
