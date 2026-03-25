# Deploy Cluster

Level 3 resource for the bootstrap skill. Contains all deploy/setup subcommands.

## setup-namespaces

Create all namespaces and apply RBAC. Idempotent.

1. Authenticate (`/authenticate`)
2. SSH to the cluster control plane
3. Apply `manifests/bootstrap/namespaces.yaml`
4. Apply `manifests/rbac/agent-rbac.yaml`
5. Verify: `kubectl get namespaces`

## setup-storage

Install Longhorn and configure storage classes. Idempotent.

1. Authenticate
2. SSH to control plane
3. Check if Longhorn is installed: `kubectl get ns longhorn-system`
4. If not: install Longhorn v1.7.3, wait for rollout
5. Ensure `longhorn` StorageClass exists with correct provisioner
6. Verify: `kubectl get sc longhorn`

## deploy-master `<cluster>`

Deploy master namespace infrastructure. Does NOT touch workstation.

1. Parse cluster name. Read `profile/config.yaml` for control plane IP.
2. **Run `generate-overlays <cluster>`** if overlays don't exist
3. **Run `setup-secrets <cluster>`** if secrets don't exist
4. Use bootstrap auth (both `.deployer-auth` and `.bootstrap-auth`)
5. SSH and apply each manifest individually with `-n master`:
   ```
   kubectl apply -n master -f alloy.yaml -f prometheus.yaml -f loki.yaml -f grafana.yaml -f datasources.yaml
   ```
   Do NOT use `kubectl apply -k` (blocked). Do NOT apply workstation.yaml.
6. Apply dashboard ConfigMaps
7. Verify pods running
8. Remove auth

## setup-kord-storage `<cluster>`

Create the shared kord PVC and initialize the git repo. Must run BEFORE `deploy-gateway`.

1. Authenticate (`/authenticate`)
2. SSH to the cluster control plane
3. Apply `manifests/gateway-kord-storage.yaml` with `-n gateway`
4. Wait for the `kord-init` Job to complete: `kubectl wait --for=condition=complete job/kord-init -n gateway --timeout=60s`
5. Verify PVC is Bound: `kubectl get pvc kord-shared -n gateway` — status should be `Bound`
6. Verify git repo exists: `kubectl exec job/kord-init -n gateway -- ls /kord-shared/.git` (or via a debug pod if the Job has completed)

## deploy-gateway `<cluster>`

Deploy the observability gateway stack.

1. Parse cluster name. Read `profile/config.yaml` for Tailscale IP.
2. **Run `generate-overlays <cluster>`** if overlays don't exist
3. **Run `setup-secrets <cluster>`** if secrets don't exist
4. SSH to cluster:
   - Create `monitor` namespace if needed
   - Copy gateway manifests (base + overlay)
   - Apply via `kubectl apply -k <overlay-dir>`
5. Verify gateway pod running

## add-node `<cluster> <node-ip>`

Add a worker node to an existing cluster.

1. Parse cluster name and node IP
2. Read `profile/config.yaml` for control plane IP and node token
3. SSH to node, install k3s agent
4. Wait for node to appear
5. Update `profile/config.yaml` — append new IP to cluster's nodes list

## add-cluster `<name> <node-ip>`

Bootstrap a new k3s cluster on a remote machine.

1. Parse cluster name and node IP
2. SSH to node, run k3s server install via `manifests/bootstrap/setup-cluster.sh`
3. Run `setup-namespaces` and `setup-storage`
4. Apply RBAC
5. Add new cluster entry to `profile/config.yaml`

## Secrets

Create Kubernetes Secrets from `pass` before deploying. Idempotent:

```bash
ssh <control-plane> "kubectl create secret generic <name> -n <namespace> \
  --from-literal=<key>=$(pass show <pass-path>) \
  --dry-run=client -o yaml | kubectl apply -f -"
```

| Secret | Namespace | pass path | Keys |
|--------|-----------|-----------|------|
| `tailscale-auth` | gateway | `kordinate/tailscale/auth_key_gateway` | `TS_AUTHKEY` |
| `minio-credentials` | gateway | `kordinate/minio/root_user`, `kordinate/minio/root_password` | `root-user`, `root-password` |
| `cloudflare-tunnel` | gateway | `kordinate/cloudflare/tunnel_token` | `TUNNEL_TOKEN` |
| `grafana-admin` | master | `kordinate/grafana_admin/password` | `admin-password` |

## Bootstrap Auth

For master namespace writes, use both auth tokens:

1. `cp profile/locks/deployer /tmp/.deployer-auth`
2. `cp profile/locks/deployer /tmp/.bootstrap-auth`
3. Run commands
4. `rm /tmp/.bootstrap-auth /tmp/.deployer-auth`

## Notes

- All SSH operations use deployer auth flow
- All subcommands are idempotent
- `deploy-master` and `deploy-gateway` create secrets and overlays automatically if needed
- After adding a cluster, deploy gateway and master stacks separately
