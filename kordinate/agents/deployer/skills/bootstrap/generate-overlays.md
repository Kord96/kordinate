# Generate Overlays

Level 3 resource for the bootstrap skill.

Read `profile/config.yaml` and generate kustomize overlays for a cluster. Base manifests use placeholders — overlays fill in cluster-specific values.

## Procedure

1. Read `$KORDINATE_HOME/profile/config.yaml`
2. Find the cluster entry matching the argument
3. For each namespace (gateway, monitor, master), generate an overlay directory:

```
manifests/<namespace>/overlays/<cluster>/
├── kustomization.yaml
└── patches/
    └── values.yaml     # cluster-specific patches
```

## Placeholder → Config Mapping

Read these from `profile/config.yaml` for the target cluster:

| Placeholder | Config path | Example |
|------------|-------------|---------|
| `REGISTRY` | `clusters.<name>.services.registry.url` | `10.95.43.66:5000` |
| `STORAGE_CLASS` | `longhorn` (constant after setup-storage) | `longhorn` |
| `MUST_BE_SET` (Tailscale auth) | `pass show kordinate/tailscale/auth_key_<purpose>` | via Secret |
| `MUST_BE_SET_BY_OVERLAY` (TS hostname) | `clusters.<name>.name` | `vandc` |
| Namespace names | `clusters.<name>.namespaces` | `[gateway, monitor, master]` |
| Tailscale IPs | `clusters.<name>.gateway_tailscale_ip` | `100.107.8.117` |
| Domain names | `network.grafana_public` | `grafana.khaledkord.com` |
| PVC sizes | Use defaults: 20Gi workstation, 50Gi loki/prom, 10Gi minio/beorn, 5Gi grafana | Override in config if needed |
| Resource limits | Use defaults from base manifests | Override in config if needed |
| Retention periods | Use defaults: 7d monitor prom, 30d master prom/loki | Override in config if needed |

## Kustomization Template

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
patches:
  - path: patches/values.yaml
```

## Notes

- Generated overlays are checked into the repo — they contain cluster-specific but non-secret values
- Secrets (Tailscale auth keys, MinIO credentials) are NOT in overlays — they're created by `setup-secrets`
- If `profile/config.yaml` changes, re-run `generate-overlays` to update
- The `generate-config.py` script in `master/` does a subset of this — it can be replaced by this procedure
