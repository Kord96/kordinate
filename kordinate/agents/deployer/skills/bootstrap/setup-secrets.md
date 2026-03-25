# Setup Secrets

Level 3 resource for the bootstrap skill.

Create Kubernetes Secrets from the `pass` store. Credentials never appear in manifests or overlays.

## Procedure

1. Read cluster info from `$KORDINATE_HOME/profile/config.yaml`
2. SSH to the cluster control plane
3. Create each Secret from `pass`:

## Required Secrets

| Secret | Namespace | pass path | Keys |
|--------|-----------|-----------|------|
| `tailscale-auth` | gateway | `kordinate/tailscale/auth_key_gateway` | `TS_AUTHKEY` |
| `minio-credentials` | gateway | `kordinate/minio/root_user`, `kordinate/minio/root_password` | `root-user`, `root-password` |
| `cloudflare-tunnel` | gateway | `kordinate/cloudflare/tunnel_token` | `TUNNEL_TOKEN` |
| `grafana-admin` | master | `kordinate/grafana_admin/password` | `admin-password` |

## Creation Command

```bash
ssh <control-plane> "kubectl create secret generic <name> -n <namespace> \
  --from-literal=<key>=$(pass show <pass-path>) \
  --dry-run=client -o yaml | kubectl apply -f -"
```

`--dry-run=client -o yaml | kubectl apply -f -` makes it idempotent — creates or updates.

## Convention

All new credentials must go through `pass`:

1. `pass insert kordinate/<service>/<key>`
2. Add to this table
3. Reference in manifests as `secretKeyRef` — never inline values

## Notes

- Run before `deploy-master` or `deploy-gateway` — pods will crash without secrets
- The `pass` store must be initialized and GPG key available on the workstation
- Secrets are cluster-scoped — re-run for each cluster
