# Monitoring Architecture

## Overview

All observability is pull-based. Each cluster is a standalone unit with its own gateway
Alloy + Prometheus + Loki. The master namespace provides a unified view by pulling from
all clusters — clusters are unaware of master.

## Data Flow

```
┌─────────────── inside each cluster ───────────────────┐
│                                                        │
│  App pods ──stdout (JSON)──┐                           │
│  App pods ──/metrics───────┤                           │
│  Kubelet ──/metrics/cadvisor─┤     Gateway Alloy       │
│  KSM ──:8080/metrics────────┘  (scrapes + tails all)  │
│                                         │              │
│                              ┌──────────┴──────────┐   │
│                              ▼                     ▼   │
│                     Gateway Prometheus      Gateway Loki│
│                        (30d retention)     (30d retention)│
└────────────────────────┬────────────────────────────────┘
                         │
              pull (read-only kubeconfigs over Tailscale)
              metrics: /federate from gateway Prometheus
              logs: tail pods via K8s API
                         │
                    Master Alloy
                    ┌────┴────┐
                    ▼         ▼
          Master Prometheus  Master Loki
                    └────┬────┘
                         ▼
                      Grafana
```

## Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Gateway Alloy | gateway ns (every cluster) | Scrapes local pods, kubelet, KSM; tails logs via K8s API |
| Gateway Prometheus | gateway ns (every cluster) | Local metrics buffer, serves /federate for master |
| Gateway Loki | gateway ns (every cluster) | Local log store (30d retention) |
| Master Alloy | master ns (one cluster) | Pulls metrics via /federate and logs via K8s API from all clusters |
| Master Prometheus | master ns | Centralized metrics store (30d), receives remote_write from master Alloy |
| Master Loki | master ns | Centralized log store (30d), receives push from master Alloy |
| Grafana | master ns | Dashboards, queries only master Prometheus + master Loki |

## App Contract

- **Metrics**: Expose `/metrics` in Prometheus format. Gateway Alloy discovers via `prometheus.io/scrape=true` pod annotation.
- **Logs**: Write structured JSON to stdout. Gateway Alloy tails via `loki.source.kubernetes` (K8s API). Required fields: `level`, `message`.
- Labels injected by Alloy: `cluster`, `namespace`, `component`, `tier`, `node`, `pod`.

## Key Principles

- Clusters are independent — if master goes down, clusters keep collecting
- If a cluster goes down, master retains historical data
- Grafana queries only master's local stores — single datasource per signal
- Nothing pushes to master — master pulls everything

## Failure Modes

| Failure | Impact | Detection |
|---------|--------|-----------|
| Gateway Alloy down | Local cluster loses new metric/log collection; master loses that cluster's data | Missing data in Grafana, pod restart count |
| Master Alloy down | Grafana stops receiving new data from all clusters; clusters unaffected | Stale data in dashboards |
| Gateway Prometheus down | Master can't federate metrics from that cluster; local Alloy has nowhere to write | Federation errors in master Alloy logs |
| Tailscale connectivity | Master can't reach remote clusters | Federation scrape failures, log tail disconnects |
