# Monitoring Infrastructure — Config & Topology

## Design Philosophy

Clusters are standalone and unaware of the master. The master pulls from clusters via Tailscale gateway. Each cluster operates independently — if the master goes down, local monitoring continues uninterrupted.

## Tailscale Gateway Topology

### Mesh Endpoints

| Cluster | Tailscale IP | Exposed Ports | Services |
|---------|-------------|---------------|----------|
| vandc | 100.107.8.117 | 9090, 3100, 6443 | Prom, Loki, K8s API |
| home | 100.113.48.89 | 9090 | Prom |

### Cross-Cluster Access Pattern

Master Alloy reaches cluster services through Tailscale IPs:
- **Metrics federation**: `GET http://<tailscale-ip>:9090/federate` (vandc, home)
- **Log tailing**: K8s API at `<tailscale-ip>:6443` via remote kubeconfig
- **Sentinel cross-namespace**: queries `gateway.gateway.svc.cluster.local:9090` (within vandc cluster)

## Service Endpoints

### Vandc Cluster — monitor namespace
| Service | Port | Retention | Notes |
|---------|------|-----------|-------|
| Gateway Alloy | — | — | Scrapes pods (prometheus.io annotations), kubelet/cAdvisor, KSM, Kafka JMX, node-exporter. Injects `cluster=vandc`. |
| Gateway Prometheus | 9090 | 3h | Short-term buffer. Exposed over Tailscale. |
| Gateway Loki | 3100 | 30d | Rate limit: 16MB/s ingestion. Exposed over Tailscale. |
| Tailscale sidecar | 9090, 3100, 6443 | — | Mesh gateway exposing Prom, Loki, K8s API |

### Master Cluster — master namespace
| Service | Port | Retention | Notes |
|---------|------|-----------|-------|
| Master Alloy | — | — | Pulls /federate from vandc (100.107.8.117:9090) and home (100.113.48.89:9090). Tails logs via remote kubeconfig. |
| Master Prometheus | 9191 | 30d | Aggregated long-term metrics storage |
| Master Loki | 3100 | 30d | Aggregated logs |
| Grafana | — | — | Reads from Master Prom and Loki. Dashboards provisioned via ConfigMaps. |

### Vandc Cluster — prod namespace
| Service | Port | Notes |
|---------|------|-------|
| Sentinel | — | Alert evaluator. Queries gateway Prom cross-namespace. 12 evaluation sections. |
| MinIO | — | Snapshot backend (SNAPSHOT_BACKEND=minio). S3-compatible. NOT scraped by Prometheus (gap). Exposes metrics at /minio/v2/metrics/cluster. |

## Config File Locations

### Monitoring Stack Configs (profile repo)
| Config | Path |
|--------|------|
| Gateway Alloy | `~/.claude/agents/deployer/manifests/monitor/base/alloy.yaml` |
| Master Alloy | `~/.claude/agents/deployer/manifests/master/base/alloy.yaml` |
| Gateway Prometheus | `~/.claude/agents/deployer/manifests/monitor/base/prometheus.yaml` |

### Application Monitoring Configs (logBD repo)
| Config | Path |
|--------|------|
| Sentinel deployment | `/home/claude/logbd/deploy/graphdb/monitoring/sentinel.yaml` |
| MinIO deployment | `/home/claude/logbd/deploy/graphdb/storage/minio.yaml` |

## Data Flow

```
Pod metrics → Gateway Alloy scrapes → Gateway Prom (3h) → Master Alloy federates → Master Prom (30d) → Grafana
Pod logs    → Gateway Alloy tails   → Gateway Loki (30d) → Master Alloy tails     → Master Loki (30d) → Grafana
```

## Sentinel Details

- **Location**: prod namespace, vandc cluster
- **Prometheus endpoint**: `gateway.gateway.svc.cluster.local:9090` (cross-namespace)
- **12 evaluation sections**: process status, ingestion, buffers, enrichment, downloads, derived, storage, dependencies, clock skew, FD exhaustion, DB sizes, composites
- **KNOWN GAP**: Does not check MinIO health (now a critical dependency after snapshot migration)

## MinIO Gap

- MinIO is deployed in prod namespace as the snapshot backend (SNAPSHOT_BACKEND=minio)
- It is NOT scraped by Prometheus — no metrics are collected
- It exposes metrics at `/minio/v2/metrics/cluster` (available but unused)
- Neither Gateway Alloy nor Sentinel monitor MinIO health
- This is a critical gap since snapshots depend entirely on MinIO availability

## Dashboard Provisioning

Grafana dashboards are provisioned via ConfigMaps (GitOps-compatible). Sauron owns dashboard content; deployer creates the ConfigMaps and patches the Grafana deployment at deploy time.

The base `grafana.yaml` is generic — no project-specific references. Dashboard volumes are added via a JSON patch from the project profile.

### Deploy flow

1. `kubectl apply -f grafana.yaml` — generic base (no dashboards)
2. Create ConfigMaps from dashboard sources:
   ```
   kubectl create configmap grafana-db-<project> --from-file=<project-repo>/monitoring/dashboards/ -n master
   kubectl create configmap grafana-db-<project>-drill --from-file=<project-repo>/monitoring/dashboards/drill/ -n master
   kubectl create configmap grafana-db-infra --from-file=~/.claude/agent-memory/sauron/dashboards/ -n master
   ```
3. `kubectl patch deployment grafana -n master --type=json -p "$(cat <project-repo>/monitoring/grafana-dashboards-patch.json)"`

### ConfigMap → source mapping

| ConfigMap | Source path | Content |
|-----------|------------|---------|
| `grafana-db-<project>` | `<project-repo>/monitoring/dashboards/*.json` | Project-specific dashboards |
| `grafana-db-<project>-drill` | `<project-repo>/monitoring/dashboards/drill/*.json` | Project drill-down dashboards |
| `grafana-db-infra` | `agent-memory/sauron/dashboards/*.json` | General infra dashboards |

## Operational Notes

- Gateway Prometheus has only 3h retention — it is a buffer, not long-term storage
- Master owns all long-term data (30d retention for both Prom and Loki)
- The `cluster` label is injected by Gateway Alloy from `CLUSTER_NAME` env var (sourced from `cluster-identity` ConfigMap)
- Federation pulls from Gateway Prom `/federate` — never add direct pod scraping to Master Alloy
