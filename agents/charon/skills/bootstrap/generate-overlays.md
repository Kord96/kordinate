# Generate Overlays

Level 3 resource for the infra skill.

Read `profile/config.yaml` and generate kustomize overlays for a cluster. Base manifests use placeholders — overlays fill in cluster-specific values.

## Procedure

1. Read `$KORDINATE_HOME/profile/config.yaml`
2. Find the cluster entry matching the argument
3. For each namespace (gateway, monitor, master), generate an overlay directory:

```
$KORDINATE_HOME/profile/overlays/<cluster>/
├── gateway/
│   ├── kustomization.yaml
│   └── patches.yaml
├── monitor/
│   ├── kustomization.yaml
│   └── patches.yaml
└── master/
    ├── kustomization.yaml
    ├── patches.yaml
    ├── workstation-caddyfile.yaml   # generated — Caddy routing config
    ├── datasources.yaml            # generated — Grafana datasource provisioning
    ├── alloy-config.yaml           # generated — cluster-specific River config
    └── gateway-registry.yaml       # generated — cluster gateway IPs
```

## Master Overlay — kord PVC

The master overlay must include a patch for the `kord` PVC to set the storageClassName. This PVC is defined in `master-kord-storage.yaml` (base manifest) with placeholder `STORAGE_CLASS`.

In the master `patches.yaml`, add:
```yaml
# Kord PVC storage
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: kord
spec:
  storageClassName: <STORAGE_CLASS>
```

The kord volume is referenced by the Workstation deployment (which runs Beorn as a background process) in its base manifest. No additional volume patches are needed unless the overlay needs to override mount paths or env vars.

## Placeholder → Config Mapping

Read from `profile/config.yaml` for the target cluster:

| Placeholder | Config path | Example |
|------------|-------------|---------|
| `REGISTRY` | `clusters.<name>.services.registry.url` | `10.95.43.66:5000` |
| `STORAGE_CLASS` | `longhorn` (constant after setup-storage) | `longhorn` |
| `MUST_BE_SET_BY_OVERLAY` (TS hostname) | `clusters.<name>.name` | `vandc` |
| Tailscale IPs | `clusters.<name>.gateway_tailscale_ip` | `100.107.8.117` |
| Domain names | `network.grafana_public` | `grafana.khaledkord.com` |
| Domain names | `network.docs_public` | `docs.khaledkord.com` |

## Derived Values (not in config.yaml)

Service DNS names follow a deterministic pattern — construct them from the namespace context:

| Value | Derivation | Example |
|-------|-----------|---------|
| Grafana URL | `grafana.<namespace>.svc.cluster.local:3000` | `grafana.master.svc.cluster.local:3000` |
| Prometheus URL | `prometheus.<namespace>.svc.cluster.local:<port>` | `prometheus.master.svc.cluster.local:9191` |
| Loki URL | `loki.<namespace>.svc.cluster.local:3100` | `loki.master.svc.cluster.local:3100` |

## Generated ConfigMaps

These are too complex for simple kustomize patches — generate the full ConfigMap in the overlay.

### workstation-caddyfile (master namespace)

Read `network.grafana_public` and `network.docs_public` from config.yaml. Construct service DNS from namespace context. Generate:
- `@grafana` host matcher → reverse proxy to `grafana.master.svc.cluster.local:3000`
- `@docs` host matcher → reverse proxy to `docs.master.svc.cluster.local:80`
- Fallback 404 handler

### grafana-datasources (master namespace)

Construct Prometheus and Loki URLs from namespace context. Generate the full provisioning ConfigMap with datasource entries.

### alloy-config (master namespace)

Read all clusters from config.yaml. For each cluster with a `gateway_tailscale_ip`, generate:
- A `prometheus.scrape` block targeting `<tailscale_ip>:9090` for metrics federation
- A `local.file_match` + `loki.source.file` block for log tailing from `/data/federate/<cluster>/*.jsonl`

The config also needs:
- `prometheus.remote_write` to `prometheus.master.svc.cluster.local:9191`
- `loki.write` to `loki.master.svc.cluster.local:3100`
- `loki.process` pipeline for JSON structured logs

### gateway-registry (master namespace)

Generate a ConfigMap with `gateways.yaml` listing all clusters and their Tailscale IPs + ports:
```yaml
gateways:
  - name: <cluster>
    tailscale_ip: "<gateway_tailscale_ip>"
    ports:
      metrics: 9090
      minio: 9000
```

## Platform Overlays

In addition to cluster infrastructure overlays, generate platform overlays for the agent runtime. These live at `profile/overlays/platform/<env>/` and customize the base manifests at `agents/charon/skills/platform/manifests/base/`.

### Procedure

1. Read `$KORDINATE_HOME/profile/config.yaml` — look for a `platform:` section with per-environment config
2. For each environment (default: `dev`), generate:

```
$KORDINATE_HOME/profile/overlays/platform/<env>/
├── kustomization.yaml      # namespace, base reference
├── scaling.yaml             # KEDA ScaledObject patches (min/max replicas, cooldown)
└── resources.yaml           # resource limit overrides (optional)
```

### kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: <env>
resources:
  - ../../../../agents/charon/skills/platform/manifests/base
patches:
  - path: scaling.yaml
  - path: resources.yaml
```

### scaling.yaml

Generate one strategic merge patch per agent from `platform.agents.<name>`:

| Config path | Patch field | Default |
|------------|------------|---------|
| `platform.agents.<name>.standby` | `spec.minReplicaCount` | 0 |
| `platform.agents.<name>.max_replicas` | `spec.maxReplicaCount` | 3 |
| `platform.agents.<name>.cooldown` | `spec.cooldownPeriod` | 300 |

### resources.yaml

Generate resource patches if `platform.agents.<name>.resources` is set. Otherwise create an empty file with a comment.

### Config Schema (platform section)

```yaml
platform:
  environments:
    dev:
      agents:
        augur:   { standby: 1, max_replicas: 10, cooldown: 300 }
        charon:  { standby: 1, max_replicas: 3,  cooldown: 300 }
        warden:  { standby: 1, max_replicas: 5,  cooldown: 180 }
        sauron:  { standby: 0, max_replicas: 3,  cooldown: 600 }
        scribe:  { standby: 0, max_replicas: 3,  cooldown: 600 }
        alfred:  { standby: 0, max_replicas: 2,  cooldown: 600 }
    prod:
      agents:
        augur:   { standby: 2, max_replicas: 15, cooldown: 180 }
        # ...
```

After generating, store via: `/kord alfred store overlay platform/<env>`.

## Notes

- Cluster overlays live at `profile/overlays/<cluster>/` — infrastructure-specific
- Platform overlays live at `profile/overlays/platform/<env>/` — agent runtime config
- Secrets (Tailscale auth keys, MinIO credentials, Anthropic API key) are NOT in overlays — created at deploy time from `pass`
- If `profile/config.yaml` changes, re-run `/bootstrap generate-overlays <cluster>` for infra and `/platform deploy <env>` for agent runtime
- Base manifests stay abstract — never edit them with cluster-specific or env-specific values
