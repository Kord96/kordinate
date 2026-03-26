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
│   ├── patches.yaml
│   └── ingress-caddyfile.yaml      # generated — Caddy routing config
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

## Master Overlay — kord-shared PVC

The master overlay must include a patch for the `kord-shared` PVC to set the storageClassName. This PVC is defined in `master-kord-storage.yaml` (base manifest) with placeholder `STORAGE_CLASS`.

In the master `patches.yaml`, add:
```yaml
# Kord shared PVC storage
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: kord-shared
spec:
  storageClassName: <STORAGE_CLASS>
```

The kord-shared volume is referenced by the Workstation deployment (which runs Beorn as a background process) in its base manifest. No additional volume patches are needed unless the overlay needs to override mount paths or env vars.

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
- `@docs` host matcher → reverse proxy to `localhost:4321`
- Fallback 404 handler

### ingress-caddyfile (gateway namespace)

Read `network.grafana_public` from config.yaml. Generate:
- `@grafana` host matcher → reverse proxy to `grafana.master.svc.cluster.local:3000`
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

## Notes

- Overlays live at `profile/overlays/<cluster>/` — profile-specific, separate from base manifests
- Secrets (Tailscale auth keys, MinIO credentials) are NOT in overlays — created at deploy time from `pass`
- If `profile/config.yaml` changes, re-run `/infra generate-overlays <cluster>` to update
- Base manifests at `manifests/` stay abstract — never edit them with cluster-specific values
