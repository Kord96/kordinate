---
name: overlay-structure
description: Overlay directory structure per cluster and how config.yaml values map to overlay files
level: 3
---

# Overlay Structure Reference

This document describes the kustomize overlay directory layout per cluster and how values from `profile/config.yaml` flow into overlay files.

## Directory Layout

Each cluster has its own overlay directory under `$KORDINATE_HOME/profile/overlays/<cluster>/`. The namespaces present depend on what the cluster runs.

```
profile/overlays/<cluster>/
  gateway/
    kustomization.yaml      # references base manifests + patches
    patches.yaml            # storage class, deployment images, env vars
    ingress-caddyfile.yaml  # optional, cluster-specific Caddy config
  monitor/
    kustomization.yaml
    patches.yaml
  master/                   # only on clusters with master namespace
    kustomization.yaml
    patches.yaml
    datasources.yaml        # Grafana data sources
    alloy-config.yaml       # generated -- cross-cluster River config
    gateway-registry.yaml   # generated -- all gateway IPs
    workstation-caddyfile.yaml  # optional
```

### Namespace Presence

- **gateway/** -- present on every cluster (required namespace).
- **monitor/** -- present if `manifests.monitor` is defined for the cluster.
- **master/** -- present only on the cluster that runs the master namespace (typically one cluster).

## Config to Overlay Mapping

Values in `profile/config.yaml` are the source of truth. Overlays consume these values in specific files and fields.

| Config value | Where it appears in overlays |
|-------------|------------------------------|
| `clusters.<name>.services.registry.url` | patches.yaml: image prefixes (`REGISTRY`) |
| `clusters.<name>.name` | patches.yaml: Tailscale hostname (`MUST_BE_SET_BY_OVERLAY`) |
| `clusters.<name>.gateway_tailscale_ip` | alloy-config.yaml: scrape targets; gateway-registry.yaml |
| `network.grafana_public` | patches.yaml: domain references |
| Storage class: `longhorn` | patches.yaml: PVC storage class |

### patches.yaml

Each namespace's `patches.yaml` contains strategic merge patches or JSON patches that override base manifest values. Common overrides:

- **Image registry prefix** -- derived from `clusters.<name>.services.registry.url`.
- **Tailscale hostname** -- derived from `clusters.<name>.name`; replaces the `MUST_BE_SET_BY_OVERLAY` placeholder in base manifests.
- **Storage class** -- sets PVC storage class to `longhorn`.
- **Environment variables** -- cluster-specific env vars for deployments.
- **Domain names** -- public domain references from `network.grafana_public`, `network.docs_public`.

### kustomization.yaml

Each namespace's `kustomization.yaml` references:

- The base manifests directory (path from `clusters.<name>.manifests.<namespace>`).
- Local patch files (`patches.yaml`, optional Caddyfile overrides).
- Any generated ConfigMaps for that namespace.

## Generated ConfigMaps

Two ConfigMaps in the master namespace are **generated** rather than simple patches. They aggregate data across all clusters.

### alloy-config (master namespace)

River configuration for Grafana Alloy, enabling cross-cluster metrics and logs federation.

- Reads ALL clusters from config.yaml.
- For each cluster with a `gateway_tailscale_ip`:
  - Generates `prometheus.scrape` blocks targeting `<gateway_tailscale_ip>:<metrics_port>`.
  - Generates `loki.source.api` blocks targeting `<gateway_tailscale_ip>:<loki_port>`.
- The resulting River config is stored as `alloy-config.yaml` in the master overlay.

### gateway-registry (master namespace)

A YAML ConfigMap listing all gateways with their Tailscale IPs and service ports.

- Reads ALL clusters from config.yaml.
- For each cluster, records:
  - Cluster name
  - `gateway_tailscale_ip`
  - Relevant service ports
- Used by master-namespace workloads that need to communicate with all gateways.

## Validation Rules

When validating overlays against config, check:

1. Every value in patches.yaml that originates from config matches the current config value.
2. alloy-config.yaml references exactly the set of clusters currently in config (no missing, no extra).
3. gateway-registry.yaml references exactly the set of clusters currently in config.
4. Overlay directories exist for all clusters defined in config.
5. Namespace subdirectories match the namespaces listed in the cluster config.
