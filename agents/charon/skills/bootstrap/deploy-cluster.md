# Deploy Cluster

Level 3 resource for the bootstrap skill. Contains all deploy/setup subcommands.

## setup-namespaces

Create all namespaces and apply RBAC. Idempotent.

1. Authenticate (`/authenticate`)
2. SSH to the cluster control plane
3. Apply `manifests/namespaces.yaml`
4. Apply `manifests/agent-rbac.yaml`
5. Verify: `kubectl get namespaces`

## setup-storage

Install Longhorn and configure storage classes. Idempotent.

1. Authenticate
2. SSH to control plane
3. Install `open-iscsi` prerequisite on all cluster nodes:
   ```
   ssh kkord@<IP> "sudo apt-get install -y open-iscsi && sudo systemctl enable --now iscsid"
   ```
   Repeat for each node in `profile/config.yaml` clusters.<name>.nodes.
   Skip nodes that are macOS/Docker VMs (e.g. colima) — they cannot run Longhorn.
4. Check if Longhorn is installed: `kubectl get ns longhorn-system`
5. If not: install Longhorn v1.7.3:
   ```
   kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.7.3/deploy/longhorn.yaml
   ```
6. Wait for rollout:
   ```
   kubectl -n longhorn-system rollout status deploy/longhorn-driver-deployer --timeout=120s
   kubectl -n longhorn-system rollout status daemonset/longhorn-manager --timeout=120s
   ```
   Note: longhorn-manager pods on nodes without `open-iscsi` will CrashLoop — this is expected.
7. Verify `longhorn` StorageClass uses the correct provisioner:
   ```
   kubectl get sc longhorn -o jsonpath='{.provisioner}'
   ```
   Must be `driver.longhorn.io`, NOT `rancher.io/local-path`.
   If wrong, delete and let Longhorn recreate it:
   ```
   kubectl delete sc longhorn
   # Longhorn manager will recreate it with the correct provisioner
   ```
8. Verify: `kubectl get sc longhorn`

## deploy-master `<cluster>`

Deploy master namespace infrastructure. Includes workstation (with Beorn inside) and kord storage.

1. Parse cluster name. Read `profile/config.yaml` for control plane IP.
2. **Run `generate-overlays <cluster>`** if overlays don't exist
3. **Run `setup-secrets <cluster>`** if secrets don't exist
4. **Run `setup-kord-storage <cluster>`** if kord PVC doesn't exist
5. Use bootstrap auth (both `.charon-auth` and `.bootstrap-auth`)
6. SSH and apply kord-storage and workstation base manifests individually:
   ```
   kubectl apply -n master -f kord-storage.yaml -f workstation.yaml
   ```
7. SSH and apply remaining master resources via kustomize overlay:
   ```
   kubectl apply -k profile/overlays/<cluster>/master/ --load-restrictor LoadRestrictionsNone
   ```
   This applies base manifests with overlay patches plus generated ConfigMaps
   (workstation-caddyfile, grafana-datasources, alloy-config, gateway-registry).
8. Apply dashboard ConfigMaps
9. Verify pods running (including workstation with Beorn on port 3100)
10. Remove auth

## setup-kord-storage `<cluster>`

Create the shared kord PVC and initialize the git repo. Must run BEFORE `deploy-master`.

1. Authenticate (`/authenticate`)
2. SSH to the cluster control plane
3. Apply `manifests/master-kord-storage.yaml` with `-n master`
4. Wait for the `kord-init` Job to complete: `kubectl wait --for=condition=complete job/kord-init -n master --timeout=60s`
5. Verify PVC is Bound: `kubectl get pvc kord -n master` — status should be `Bound`
6. Verify git repo exists: `kubectl exec job/kord-init -n master -- ls /kord/kordinate/.git` (or via a debug pod if the Job has completed)

## deploy-gateway `<cluster>`

Deploy the observability gateway stack.

1. Parse cluster name. Read `profile/config.yaml` for Tailscale IP.
2. **Run `generate-overlays <cluster>`** if overlays don't exist
3. **Run `setup-secrets <cluster>`** if secrets don't exist
4. SSH to cluster:
   - Create `gateway` namespace if needed
   - Copy gateway manifests (base + overlay)
   - Apply via `kubectl apply -k <overlay-dir>`
5. Verify gateway pod running

## add-node `<cluster> <node-ip>`

Add a worker node to an existing cluster. Installs Tailscale with an ephemeral key so the
node can reach the control plane over the tailnet, then joins it as a k3s agent.
Ephemeral nodes auto-deregister from Tailscale when they go offline — no device pollution.

1. Parse cluster name and node IP (the node's reachable IP for initial SSH)
2. Read `profile/config.yaml` for control plane Tailscale IP and node token
3. SSH to node, install Tailscale:
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   TS_KEY=$(pass show kordinate/tailscale/auth_key_worker)
   sudo tailscale up --authkey="$TS_KEY" --hostname="k3s-worker-$(hostname -s)"
   ```
   The key in pass must be **ephemeral** and **pre-authorized** (create via Tailscale
   admin console or API with `"ephemeral": true, "preauthorized": true`).
4. Verify Tailscale is connected and can reach control plane:
   ```bash
   tailscale ping <control-plane-tailscale-ip>
   ```
5. SSH to node, install k3s agent pointing at control plane's **Tailscale IP**:
   ```bash
   curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="agent" sh -s - \
     --server "https://<control-plane-tailscale-ip>:6443" \
     --token "<node-token>" \
     --node-ip "$(tailscale ip -4)" \
     --node-name "$(hostname -s)"
   ```
   Using `tailscale ip -4` as `--node-ip` so k3s traffic flows over the tailnet.
6. Wait for node to appear: `kubectl get nodes` on control plane
7. Update `profile/config.yaml` — append new entry to cluster's nodes list with both
   the initial SSH IP and the Tailscale IP

## add-cluster `<name> <node-ip>`

Bootstrap a new k3s cluster on a remote machine.

1. Parse cluster name and node IP
2. SSH to node, run k3s server install via `setup-cluster.sh`
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
| `gateway-tailscale` | gateway | `kordinate/tailscale/auth_key_gateway` | `TS_AUTHKEY` |
| *(host-level)* | — | `kordinate/tailscale/auth_key_worker` | Ephemeral pre-auth key for worker nodes (not a k8s Secret) |
| `minio-credentials` | gateway | `kordinate/minio/root_user`, `kordinate/minio/root_password` | `root-user`, `root-password` |
| `cloudflared-tunnel` | master | `kordinate/cloudflare/tunnel_token` | `TUNNEL_TOKEN` |
| `grafana-admin` | master | `kordinate/grafana_admin/password` | `admin-password` |

## Bootstrap Auth

For master namespace writes, use both auth tokens:

1. `cp profile/locks/charon /tmp/.charon-auth`
2. `cp profile/locks/charon /tmp/.bootstrap-auth`
3. Run commands
4. `rm /tmp/.bootstrap-auth /tmp/.charon-auth`

## Notes

- All SSH operations use charon auth flow
- All subcommands are idempotent
- `deploy-master` and `deploy-gateway` create secrets and overlays automatically if needed
- After adding a cluster, deploy gateway and master stacks separately
