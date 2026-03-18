# Infrastructure Guide

> **For your specific cluster topology, see `profile/topology.yaml`.**

## Overview

Each k3s cluster is a standalone Kubernetes installation with its own control plane,
worker nodes, and observability stack. Clusters connect over Tailscale but operate
independently — no cluster depends on any other.

The `master` namespace provides a unified view across all clusters. It lives on one
cluster but is logically separate — it pulls data from clusters, clusters don't
push to it.

```
┌─ cluster-a ─────────────────────────────────┐
│                                              │
│  Apps ──▶ Gateway Alloy ──▶ Gateway Prom/Loki│
│   │           ▲                              │
│   └─ stdout ──┘ via K8s API                  │
│                                              │
└──────────────────────────────────────────────┘
                   ▲
                   │
                   │ pull (metrics + logs via Gateway Tailscale)
                   │
┌──────────────────┴───────────────────────────┐
│                                     master   │
│                                              │
│  Master Alloy ──▶ Master Prom/Loki           │
│                          │                   │
│                          ▼                   │
│                       Grafana                │
│                                              │
└──────────────────┬───────────────────────────┘
                   │
                   │ pull (metrics + logs via Gateway Tailscale)
                   │
                   ▼
┌──────────────────────────────────────────────┐
│                             cluster-b        │
│                                              │
│  Apps ──▶ Gateway Alloy ──▶ Gateway Prom/Loki│
│   │           ▲                              │
│   └─ stdout ──┘ via K8s API                  │
│                                              │
└──────────────────────────────────────────────┘
```

## How data flows

All observability is **pull-based**. The gateway is the cluster's single external interface — master pulls metrics and logs through it via Tailscale. Clusters are unaware of master.

**Inside each cluster**, Gateway Alloy collects everything and writes to Gateway Prom/Loki:

```
┌────────────────────────────── inside each cluster ──────────────────────────────┐
│                                                                                 │
│  ┌── App pods ──────┐  ┌── Kubelet ─────────┐  ┌── KSM ──────────┐             │
│  │ stdout (JSON)    │  │ /metrics/cadvisor   │  │ :8080/metrics   │             │
│  │ /metrics         │  │ volume stats        │  │                 │             │
│  └────────┬─────────┘  └─────────┬───────────┘  └────────┬────────┘             │
│           │                      │                       │                      │
│           │ pull                 │ pull                   │ pull                 │
│           ▼                      ▼                       ▼                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐     │
│  │ Gateway Alloy                                                          │     │
│  │                                                                        │     │
│  │  metrics ◀── scrapes /metrics from pods, kubelet, KSM                  │     │
│  │  logs    ◀── tails pod stdout via K8s API (loki.source.kubernetes)     │     │
│  │  normalize ── drops raw kube_*/kafka_*, keeps pipeline_* + app metrics │     │
│  └──────────┬──────────────────────┬──────────────────────────────────────┘     │
│             │                      │                                            │
│             ▼                      ▼                                            │
│  ┌──────────────────┐  ┌──────────────────┐                                     │
│  │ Gateway Prom     │  │ Gateway Loki     │                                     │
│  │ (3h buffer)      │  │ (3h buffer)      │                                     │
│  └──────────────────┘  └──────────────────┘                                     │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Master pulls from each cluster's gateway** — metrics via Prometheus federation, logs via K8s API (exposed through Gateway Tailscale):

```
┌──────────────────────────────────────────────────────────────────────┐
│ Master Alloy                                                        │
│                                                                     │
│  metrics ◀── pulls Gateway Prom /federate (all series)              │
│  logs    ◀── tails pods via K8s API (through Gateway Tailscale)     │
└──────────┬──────────────────────┬───────────────────────────────────┘
           │                      │
           ▼                      ▼
┌──────────────────┐  ┌──────────────────┐
│ Master Prom      │  │ Master Loki      │
│ (30d retention)  │  │ (30d retention)  │
└────────┬─────────┘  └────────┬─────────┘
         └────────────┬────────┘
                      ▼
               ┌───────────┐
               │  Grafana  │
               └───────────┘
```

**Key principles:**
- Gateway is the cluster's single external interface — all external access goes through Gateway Tailscale
- Master pulls from gateways — clusters are unaware of master
- Both clusters are treated identically by master (symmetric design)
- Apps write structured JSON to stdout — Gateway Alloy tails via K8s API
- Apps expose `/metrics` — Gateway Alloy discovers and scrapes via pod annotations
- Gateway Alloy normalizes metrics before writing to Gateway Prom (drops raw `kube_*`/`kafka_*`, keeps `pipeline_*`)
- If master goes down, clusters keep collecting
- If a cluster goes down, master retains historical data
- Grafana queries only master's local stores — single datasource per signal

### Pod Label Taxonomy

| Label | Meaning | Source |
|-------|---------|--------|
| `app` | Project grouping | Pod label (required by app contract) |
| `pod` | Individual pod identity | Auto-injected by Alloy from K8s metadata |
| `namespace` | Environment (dev/test/prod) or system namespace | Auto-injected by Alloy from K8s metadata |
| `node` | Kubernetes node the pod runs on | Auto-injected by Alloy from K8s metadata |
| `cluster` | Cluster name (per topology) | Injected by Alloy from CLUSTER_NAME env |
| `component` | Service name (optional) | Pod label, propagated by Alloy |
| `tier` | Operational role (optional) | Pod label, propagated by Alloy |

`app` values are defined in `profile/topology.yaml`. Example categories:
- `<product-app>` — product workload pods
- `<platform-app>` — user-managed shared services (message queues, databases, caches)
- `<system-app>` — system-critical infrastructure managed by deployer

### Log shipping

Prometheus has a `/federate` endpoint for pulling metrics between instances. Loki has no equivalent — there is no pull-based log replication.

Workaround: Master Alloy tails pod logs on each cluster via the **K8s API** (`loki.source.kubernetes`), exposed through Gateway Tailscale. Each cluster's Gateway Alloy independently tails the same pods for local Gateway Loki — the two collectors are unaware of each other.

Logs are tailed twice (once locally, once by master). This is acceptable: clusters remain self-contained, master is independently resilient, and the K8s API log endpoint is lightweight (reads from kubelet's on-disk log files).

### Observability Signals

| Signal | Source | Direction | Metrics / Examples | Labels |
|--------|--------|-----------|-------------------|--------|
| App metrics | App pods (`/metrics`) | Pull (annotation-based discovery) | App-defined: request rate, error count, queue depth, cache hit ratio, health gauges | app, namespace, node, pod, cluster |
| App logs | Pod stdout (JSON) | Pull (K8s API tail) | Structured JSON: level, message, consumer, trace context | app, namespace, node, pod, container, level, consumer, cluster |
| Container resources | Kubelet cAdvisor (`/metrics/cadvisor`) | Pull (all nodes) | `container_cpu_usage_seconds_total`, `container_memory_working_set_bytes` | node, cluster |
| PVC storage | Kubelet (`/metrics`) | Pull (all nodes) | `pipeline_pvc_used_bytes`, `pipeline_pvc_capacity_bytes` (normalized from `kubelet_volume_stats_*`) | namespace, persistentvolumeclaim, node, cluster |
| Cluster state | KSM (`:8080/metrics`) | Pull | `pipeline_container_restarts_total`, `pipeline_cronjob_suspended`, `pipeline_cronjob_next_schedule_time` (normalized from `kube_*`) | namespace, pod, cluster |
| Kafka storage | Kafka JMX (`:9309`) | Pull | `pipeline_kafka_topic_size_bytes` (normalized from `kafka_log_log_size`) | topic, cluster |
| Host metrics | node-exporter DaemonSet (`:9100/metrics`) | Pull (annotation-based discovery) | `node_cpu_seconds_total`, `node_memory_MemTotal_bytes`, `node_memory_MemAvailable_bytes`, `node_filesystem_*`, `node_disk_*`, `node_network_*` | app=kord-infra, node, cluster |

## Manifests

Two categories: **framework** (owned by deployer, essential for every cluster) and **profile** (user-specific).

### Framework (deployer-owned)

Manifests live in `agents/deployer/manifests/`.

| Namespace | Contents |
|-----------|----------|
| `gateway` | Alloy, Prometheus DB, Loki DB, KSM, Tailscale (every cluster) |
| `master` | Master Alloy, Prometheus, Loki, Grafana, Workstation (one cluster only) |
| `bootstrap` | k3s install, namespaces, Longhorn, RBAC |

### Profile (user-owned)

User-specific services and config. Manifests live in `profile/additions/`.

| Directory | Contents |
|-----------|----------|
| (flat) | Platform services + personal additions (Kafka, Postgres, Redis, Cloudflare, etc.) |

### Configuration

Cluster-specific details (IPs, nodes, credentials) are in `profile/`:
- `profile/config.yaml` — cluster IPs, hostnames, service ports, API endpoints
- `pass` store (`kordinate/`) — credentials (GPG-encrypted, accessed via `pass show`/`pass insert`)
