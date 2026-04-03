---
description: Monitoring Infrastructure Topology
---
# Monitoring Topology

Canonical source: `memory/global/infra-atlas.json` (observability section).
This file documents the monitoring architecture and operational patterns.

## Stack Overview

| Component | Namespace | Endpoint | Purpose |
|-----------|-----------|----------|---------|
| Alloy | `monitor` | -- | Collects agent logs from kord namespace, ships to Loki |
| Alloy | `master` | -- | Aggregates metrics + logs from all sources |
| Prometheus | `master` | `prometheus.master.svc.cluster.local:9090` | Metrics store (30d retention) |
| Loki | `master` | `loki.master.svc.cluster.local:3100` | Log store (30d retention) |
| Grafana | `master` | `grafana.master.svc.cluster.local:3000` | Dashboards (external: `grafana.khaledkord.com`) |

## Data Flow

```
Agent pods (kord) -> monitor Alloy collects logs -> Loki (master)
App pods (/metrics) -> master Alloy scrapes (annotation-based) -> Prometheus (master)
Pod stdout (JSON) -> master Alloy tails -> Loki (master)
Grafana reads from Prometheus + Loki in master namespace
```

Agent logs flow through the `monitor` namespace Alloy, which ships them to Loki in `master`.
Application metrics use annotation-based discovery (`prometheus.io/scrape=true`).

## Alloy Deployment

Two Alloy instances serve different roles:

- **monitor/Alloy** -- Dedicated to collecting agent platform logs from the `kord` namespace. Ships structured JSON logs to Loki in master.
- **master/Alloy** -- Handles metrics scraping (annotation-based pod discovery, kubelet/cAdvisor, KSM, node-exporter) and log tailing. Writes to local Prometheus and Loki.

## Vitals Model

Vitals are **standalone deployments** (one per app, not sidecars):
- Port 9131, health gauges: `vitals_<section>{check}` (tri-state: 0=FAIL, 1=WARNING, 2=OK)
- Queries Prometheus + Loki for app-level health evaluation
- Required evaluations: `process`, `deps`
- Meta-alert: `VitalsMissing: absent(vitals_process{app='<name>'}) for 5m`

Env vars per vitals deployment:
- `PROMETHEUS_URL=http://prometheus.master.svc.cluster.local:9191`
- `LOKI_URL=http://loki.master.svc.cluster.local:3100`
- `APP_NAME=<app label>`

## Ownership

| Domain | Owner |
|--------|-------|
| Dashboard JSON content, alert rule design | **Sauron** |
| Monitoring infrastructure deployment | **Charon** |
| Grafana credentials | **Alfred** (via pass store) |

## Dashboard Provisioning

Dashboards are provisioned via ConfigMaps (GitOps-compatible):

1. `kubectl apply -f grafana.yaml` -- generic base (no dashboards)
2. Create ConfigMaps from dashboard JSON sources in master namespace
3. Patch Grafana deployment to mount the ConfigMap volumes

| ConfigMap | Source | Content |
|-----------|--------|---------|
| `grafana-db-<project>` | `<project-repo>/monitoring/dashboards/*.json` | Project dashboards |
| `grafana-db-<project>-drill` | `<project-repo>/monitoring/dashboards/drill/*.json` | Drill-down dashboards |
| `grafana-db-infra` | Sauron's dashboard memory | Infrastructure dashboards |

Sauron owns dashboard content. Charon creates ConfigMaps and patches the Grafana deployment.

## Observability Signals

| Signal | Source | Collection |
|--------|--------|------------|
| App metrics | Pod `/metrics` | Pull, annotation-based discovery |
| App logs | Pod stdout (JSON) | Pull, K8s API tail |
| Container resources | Kubelet cAdvisor | Pull, all nodes |
| Cluster state | KSM `:8080/metrics` | Pull |
| Host metrics | node-exporter `:9100` | Pull, DaemonSet |

Required log fields: `level`, `component`, `event`, `timestamp`.
Required labels: `app` (pod label, used by Alloy for discovery).

## Operational Notes

- Scrape discovery is annotation-based -- add `prometheus.io/scrape: "true"` and `prometheus.io/port` to pod annotations
- The `cluster` label is injected by Alloy from `CLUSTER_NAME` env (sourced from `cluster-identity` ConfigMap)
- Cluster is `homeserver` (ottawa) -- single-cluster setup, no federation needed
- See infra-atlas `new_workload_contract` for full observability requirements on new workloads
