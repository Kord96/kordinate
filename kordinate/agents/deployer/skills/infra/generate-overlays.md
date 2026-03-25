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
    ├── alloy-config.yaml       # generated — cluster-specific River config
    └── gateway-registry.yaml   # generated — cluster gateway IPs
```

## Placeholder → Config Mapping

Read from `profile/config.yaml` for the target cluster:

| Placeholder | Config path | Example |
|------------|-------------|---------|
| `REGISTRY` | `clusters.<name>.services.registry.url` | `10.95.43.66:5000` |
| `STORAGE_CLASS` | `longhorn` (constant after setup-storage) | `longhorn` |
| `MUST_BE_SET_BY_OVERLAY` (TS hostname) | `clusters.<name>.name` | `vandc` |
| Tailscale IPs | `clusters.<name>.gateway_tailscale_ip` | `100.107.8.117` |
| Domain names | `network.grafana_public` | `grafana.khaledkord.com` |

## Generated ConfigMaps

These are too complex for simple kustomize patches — generate the full ConfigMap in the overlay.

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
