---
description: Infrastructure Reference
---
# Infrastructure Reference

For cluster-specific details, see `profile/config.yaml` and `profile/topology.yaml`.

## Architecture

- Each k3s cluster is standalone with its own observability stack
- Clusters connect over Tailscale, operate independently
- `master` namespace provides unified cross-cluster view (one cluster only)
- All observability is pull-based — master pulls from cluster gateways

## Namespaces

| Namespace | What runs there | Scope |
|-----------|----------------|-------|
| `gateway` | Gateway Tailscale, Ingress, MinIO | Every cluster |
| `monitor` | Alloy, Prometheus, Loki, KSM, node-exporter | Every cluster |
| `master` | Master Alloy, Prometheus (30d), Loki (30d), Grafana, Workstation (with Beorn) | One cluster |
| `dev`, `test`, `prod` | Application workloads | Every cluster |

## Data Flow

Inside each cluster: Gateway Alloy scrapes app pods (/metrics), kubelet (cAdvisor), KSM, and tails pod stdout via K8s API locally. Writes to Gateway Prom and Gateway Loki.

Master: Master Alloy pulls Gateway Prom via :9090 /federate (metrics) through Gateway Tailscale. For logs, a sidecar in each cluster's Loki pod queries local Loki every 60s and writes JSON Lines files to a MinIO bucket in the gateway namespace (1 hour retention, auto-cleaned). Gateway Tailscale exposes MinIO on :9000. A puller sidecar on master fetches from each gateway's MinIO via Tailscale :9000, writes to a local emptyDir volume, and master Alloy tails the files with loki.source.file — labels preserved in JSON Lines format, re-extracted by master Alloy's loki.process pipeline. Pull-based: master reads at its own pace, no K8s API from master. Writes to Master Prom and Master Loki (30d retention). Grafana queries only master's local stores.

## Pod Labels

| Label | Source | Required |
|-------|--------|----------|
| `app` | Pod label | yes (app contract) |
| `pod` | Auto-injected by Alloy (K8s metadata) | auto |
| `namespace` | Auto-injected by Alloy | auto |
| `node` | Auto-injected by Alloy | auto |
| `cluster` | Injected by Alloy from CLUSTER_NAME env | auto |
| `component` | Pod label (optional) | no |
| `tier` | Pod label (optional) | no |

`app` values defined in `profile/topology.yaml`:
- `<product-app>` — product workload pods
- `<platform-app>` — user-managed shared services (message queues, databases, caches)
- `<system-app>` — system-critical infrastructure managed by deployer

## Observability Signals

| Signal | Source | Collection |
|--------|--------|------------|
| App metrics | Pod /metrics | Pull, annotation-based discovery |
| App logs | Pod stdout (JSON) | Pull, K8s API tail locally |
| Container resources | Kubelet cAdvisor | Pull, all nodes |
| PVC storage | Kubelet metrics | Pull, normalized as pipeline_pvc_* |
| Cluster state | KSM :8080/metrics | Pull, normalized as pipeline_* |
| Kafka storage | JMX :9309 | Pull, normalized as pipeline_kafka_* |
| Host metrics | node-exporter :9100 | Pull, DaemonSet |

## Log Shipping

Prometheus: /federate for metrics pull (:9090). Loki: sidecar in each Loki pod queries local Loki every 60s, writes JSON Lines to MinIO in gateway namespace (1 hour retention, auto-cleaned). Gateway Tailscale exposes MinIO on :9000. Master puller sidecar fetches from MinIO, writes to local volume, master Alloy tails with loki.source.file. Labels preserved in JSON Lines, re-extracted by master Alloy's loki.process pipeline. Pull-based, no K8s API from master.

## Manifests

Framework manifests: `agents/charon/manifests/`
User manifests: `profile/additions/`

## Credentials

`profile/config.yaml` — cluster IPs, hostnames, service ports
`pass` store (`kordinate/`) — GPG-encrypted, accessed via `pass show`/`pass insert`

## Constraints

- No DaemonSet except node-exporter
- No NodePorts — all services use ClusterIP
- No hostNetwork
- Gateway Alloy normalizes metrics: drops raw kube_*/kafka_*, keeps pipeline_* + app metrics
