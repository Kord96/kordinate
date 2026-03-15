# Infrastructure Monitoring Data Flow

## Architecture

Each k3s cluster is standalone with its own observability stack in the `gateway` namespace:
- **Gateway Alloy** — scrapes all pods, nodes, kubelet, KSM in the cluster
- **Gateway Prometheus** — receives metrics from gateway Alloy, retains 30d
- **Gateway Loki** — receives logs from gateway Alloy, retains 30d
- **KSM** — kube-state-metrics, scraped by gateway Alloy

## Master Namespace

The `master` namespace (one cluster only) provides a unified cross-cluster view:

- **Master Prometheus** — FEDERATES from all gateway Prometheus instances. It does NOT directly scrape pods. This is the single datasource for Grafana.
- **Master Alloy** — handles ONLY logs (tails pods via K8s API, writes to Master Loki). No metrics scraping.
- **Master Loki** — receives logs from Master Alloy.
- **Grafana** — queries only master's local Prometheus and Loki.

## Data Flow

```
VanDC cluster:
  pods/nodes → Gateway Alloy (scrape) → Gateway Prometheus (30d buffer)
                                              ↓ federate
                                     Master Prometheus (unified view)

Home cluster:
  pods/nodes → Gateway Alloy (scrape) → Gateway Prometheus (30d buffer)
                                              ↓ federate
                                     Master Prometheus (unified view)

Logs (home only):
  pods → Master Alloy (K8s API tail) → Master Loki
```

## Cluster Label

The `cluster` label is injected by each gateway Alloy via the `CLUSTER_NAME` environment variable, sourced from a `cluster-identity` ConfigMap that the deployer sets per cluster (e.g., `vandc`, `home`).

## Rules

- **Never remove federation jobs** (`federate-vandc`, `federate-home`) from Master Prometheus — this is the only path for metrics to reach the unified view.
- **Never add direct pod/node scraping to Master Alloy** — gateways already collect everything. Adding direct scrapes creates duplicate ingestion with conflicting labels.
- **Master Alloy is logs-only** — if you need to change metrics collection, modify the gateway Alloy config, not master.
- When in doubt about data flow, consult deployer: `/consult deployer "explain the monitoring data flow for <component>"`.
