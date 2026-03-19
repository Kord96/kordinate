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
| `gateway` | Gateway Tailscale, Workstation (if interactive cluster), Ingress | Every cluster |
| `monitor` | Alloy, Prometheus, Loki, KSM, node-exporter | Every cluster |
| `master` | Master Alloy, Prometheus (30d), Loki (30d), Grafana | One cluster |
| `dev`, `test`, `prod` | Application workloads | Every cluster |

## Data Flow

Inside each cluster: Gateway Alloy scrapes app pods (/metrics), kubelet (cAdvisor), KSM, and tails pod stdout via K8s API locally. Writes to Gateway Prom and Gateway Loki.

Master: Master Alloy pulls Gateway Prom via :9090 /federate (metrics) and Gateway Loki via :3101 /federate (logs) through Gateway Tailscale — symmetric pull, no K8s API from master. Writes to Master Prom and Master Loki (30d retention). Grafana queries only master's local stores. Logs are collected once by Gateway Alloy — master reads from Gateway Loki, no duplicate tailing.

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

Prometheus: /federate for metrics pull (:9090). Loki: Master Alloy pulls from Gateway Loki via :3101 /federate. Logs are collected once by Gateway Alloy and stored in Gateway Loki — master pulls from there via federation. No duplicate tailing, no K8s API from master.

## Manifests

Framework manifests: `agents/deployer/manifests/`
User manifests: `profile/additions/`

## Credentials

`profile/config.yaml` — cluster IPs, hostnames, service ports
`pass` store (`kordinate/`) — GPG-encrypted, accessed via `pass show`/`pass insert`

## Constraints

- No DaemonSet except node-exporter
- No NodePorts — all services use ClusterIP
- No hostNetwork
- Gateway Alloy normalizes metrics: drops raw kube_*/kafka_*, keeps pipeline_* + app metrics
