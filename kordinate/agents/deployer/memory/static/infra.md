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
| `gateway` (monitor) | Alloy, Prometheus (3h), Loki (3h), KSM, node-exporter, Tailscale | Every cluster |
| `master` | Master Alloy, Prometheus (30d), Loki (30d), Grafana, Workstation | One cluster |
| `dev`, `test`, `prod` | Application workloads | Every cluster |

## Data Flow

Inside each cluster: Gateway Alloy scrapes app pods (/metrics), kubelet (cAdvisor), KSM, and tails pod stdout via K8s API. Writes to Gateway Prom and Gateway Loki (3h buffer).

Master: Master Alloy pulls Gateway Prom via /federate and tails pod logs via K8s API through Gateway Tailscale. Writes to Master Prom and Master Loki (30d retention). Grafana queries only master's local stores.

## Pod Labels

| Label | Source | Required |
|-------|--------|----------|
| `app` | Pod label | yes (app contract) |
| `pod` | Auto-injected by Alloy (K8s metadata) | auto |
| `namespace` | Auto-injected by Alloy | auto |
| `node` | Auto-injected by Alloy | auto |
| `cluster` | Injected by Alloy from CLUSTER_NAME env | auto |
| `component` | Pod label (optional) | no |

## Observability Signals

| Signal | Source | Collection |
|--------|--------|------------|
| App metrics | Pod /metrics | Pull, annotation-based discovery |
| App logs | Pod stdout (JSON) | Pull, K8s API tail |
| Container resources | Kubelet cAdvisor | Pull, all nodes |
| PVC storage | Kubelet metrics | Pull, normalized as pipeline_pvc_* |
| Cluster state | KSM :8080/metrics | Pull, normalized as pipeline_* |
| Kafka storage | JMX :9309 | Pull, normalized as pipeline_kafka_* |
| Host metrics | node-exporter :9100 | Pull, DaemonSet |

## Manifests

Framework manifests: `agents/deployer/manifests/`
User manifests: `profile/additions/`

## Constraints

- No DaemonSet except node-exporter
- No NodePorts — all services use ClusterIP
- No hostNetwork
- Gateway Alloy normalizes metrics: drops raw kube_*/kafka_*, keeps pipeline_* + app metrics
