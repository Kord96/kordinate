# Monitoring Architecture (Multi-Cluster)

## Design Philosophy

Clusters are standalone and unaware of the master. The master pulls from clusters via Tailscale gateway. This decoupled design means each cluster can operate independently — if the master goes down, local monitoring (Gateway Prometheus, Gateway Loki) continues uninterrupted. The master is a read-only aggregator.

## Architecture Overview

### Two-Tier Model

**Tier 1 — Cluster-Local (per cluster)**
- Gateway Alloy: scrapes all pods, kubelet/cAdvisor, kube-state-metrics, Kafka JMX, node-exporter. Injects cluster label. Writes to local Prometheus (remote_write) and pushes logs to local Loki.
- Gateway Prometheus: 3h retention, short-term buffer only.
- Gateway Loki: 30d retention, 16MB/s ingestion rate limit.
- Tailscale sidecar: exposes Prom:9090, Loki:3100, K8s API:6443 over Tailscale mesh.

**Tier 2 — Master Aggregator**
- Master Alloy: pulls /federate from all cluster Proms via Tailscale. Tails logs from all clusters via remote kubeconfig over Tailscale. Writes to Master Prom and Master Loki.
- Master Prometheus: 30d retention, aggregated long-term storage.
- Master Loki: 30d retention, aggregated logs.
- Grafana: reads from Master Prom and Loki. Dashboards provisioned via ConfigMaps.

### Data Flow

```
Pod metrics → Gateway Alloy scrapes → Gateway Prom (3h) → Master Alloy federates → Master Prom (30d) → Grafana
Pod logs    → Gateway Alloy tails   → Gateway Loki (30d) → Master Alloy tails     → Master Loki (30d) → Grafana
```

### Components by Namespace

| Component | Namespace | Cluster | Purpose |
|-----------|-----------|---------|---------|
| Gateway Alloy | monitor | vandc | Scrape + forward |
| Gateway Prometheus | monitor | vandc | 3h local buffer |
| Gateway Loki | monitor | vandc | 30d local logs |
| Tailscale sidecar | monitor | vandc | Mesh exposure |
| Master Alloy | master | master | Federate + aggregate |
| Master Prometheus | master | master | 30d aggregated metrics |
| Master Loki | master | master | 30d aggregated logs |
| Grafana | master | master | Visualization |
| Sentinel | prod | vandc | Alert evaluation |
| MinIO | prod | vandc | Snapshot storage (S3) |

### Tailscale Mesh Endpoints

| Cluster | Tailscale IP | Exposed Ports |
|---------|-------------|---------------|
| vandc | 100.107.8.117 | Prom:9090, Loki:3100, K8s API:6443 |
| home | 100.113.48.89 | Prom:9090 |

### Sentinel (Alerting)

- Runs in prod namespace, queries Gateway Prometheus cross-namespace
- 12 evaluation sections: process status, ingestion, buffers, enrichment, downloads, derived, storage, dependencies, clock skew, FD exhaustion, DB sizes, composites

### Known Architectural Gaps

1. **MinIO not monitored**: MinIO (prod namespace) is a critical dependency after snapshot migration (SNAPSHOT_BACKEND=minio) but is NOT scraped by Prometheus. It exposes metrics at /minio/v2/metrics/cluster — available but unused.
2. **Sentinel does not check MinIO health**: no MinIO evaluation section exists.

### Design Decisions

- **Tailscale over VPN tunnels**: zero-config mesh, no port forwarding, works across NAT.
- **Federation over remote_write**: master pulls rather than clusters pushing — clusters stay autonomous.
- **Short local retention (3h)**: clusters are not storage targets; master owns long-term data.
- **ConfigMap-provisioned dashboards**: GitOps-compatible, no manual Grafana state.
