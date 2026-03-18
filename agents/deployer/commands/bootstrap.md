# bootstrap

Manage cluster infrastructure: namespaces, storage, stacks, nodes, clusters.

## Arguments

`$ARGUMENTS` — Required format: `<subcommand> [args]`

## Subcommands

### setup-namespaces

Create all namespaces and apply RBAC. Idempotent — safe to re-run.

1. Use standard deployer auth (`.deployer-auth`).
2. SSH to the cluster control plane.
3. Apply `agents/deployer/manifests/bootstrap/namespaces.yaml`.
4. Apply `agents/deployer/manifests/rbac/agent-rbac.yaml`.
5. Verify: `kubectl get namespaces`.

### setup-storage

Install Longhorn and configure storage classes. Idempotent.

1. Use standard deployer auth (`.deployer-auth`).
2. SSH to the cluster control plane.
3. Check if Longhorn is already installed: `kubectl get ns longhorn-system`.
4. If not installed:
   ```
   kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.7.3/deploy/longhorn.yaml
   kubectl -n longhorn-system rollout status deploy/longhorn-driver-deployer --timeout=300s
   kubectl -n longhorn-system rollout status deploy/longhorn-ui --timeout=300s
   ```
5. Ensure a `longhorn` StorageClass exists with `provisioner: driver.longhorn.io` and `reclaimPolicy: Retain`. If a stale StorageClass named `longhorn` exists with `provisioner: rancher.io/local-path`, delete it first so Longhorn's default takes over.
6. Verify: `kubectl get sc longhorn`.

### deploy-master `<cluster>`

Deploy master namespace infrastructure (Grafana, Prometheus, Loki, Alloy, Ingress) to a cluster. Does NOT touch workstation — workstation is deployed by the root CLI only.

1. Parse cluster name from `$ARGUMENTS`.
2. Read `~/.claude/profile/config.yaml` to get the cluster's control plane IP.
3. **Use bootstrap auth** (see Authentication section — both `.deployer-auth` and `.bootstrap-auth`).
4. SSH to the cluster node and apply each manifest individually with `-n master`:
   ```
   kubectl apply -n master -f alloy.yaml -f prometheus.yaml -f loki.yaml -f grafana.yaml -f ingress.yaml -f datasources.yaml
   ```
   Do NOT use `kubectl apply -k` (blocked — includes workstation.yaml). Do NOT apply workstation.yaml (always blocked).
5. Apply any dashboard ConfigMaps.
6. Verify pods are running.
7. **Remove bootstrap auth** (`rm /tmp/.bootstrap-auth /tmp/.deployer-auth`).

### deploy-gateway `<cluster>`

Deploy the observability gateway stack to a cluster.

1. Parse cluster name from `$ARGUMENTS`.
2. Read `~/.claude/profile/config.yaml` to get the cluster's Tailscale IP.
3. Check for a matching overlay in `agents/deployer/manifests/monitor/overlays/<cluster>/`. If none exists, create one from the template (patch cluster name and Tailscale hostname).
4. Prompt for Tailscale auth key (or read from `pass show kordinate/tailscale/auth_key_gateway`).
5. SSH to the cluster node:
   - Create the `monitor` namespace (if not exists).
   - Create the `tailscale-auth` secret with the auth key.
   - Copy gateway manifests (base + overlay) to the node.
   - Apply via `kubectl apply -k <overlay-dir>`.
6. Verify gateway pod is running.

### add-node `<cluster> <node-ip>`

Add a worker node to an existing cluster.

1. Parse cluster name and node IP from `$ARGUMENTS`.
2. Read `~/.claude/profile/config.yaml` to get the cluster's control plane IP and node token.
3. SSH to `<node-ip>` and run the k3s agent install:
   ```
   ssh <node-ip> "curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC=agent sh -s - \
     --server https://<control-plane-ip>:6443 --token <token> \
     --node-ip <node-ip> --node-name <hostname>"
   ```
4. Wait for the node to appear: `kubectl get nodes` (via SSH to control plane).
5. Update `~/.claude/profile/config.yaml` — append the new IP to the cluster's `nodes` list.
6. Commit and push the config change.

### add-cluster `<name> <node-ip>`

Bootstrap a new k3s cluster on a remote machine.

1. Parse cluster name and node IP from `$ARGUMENTS`.
2. SSH to `<node-ip>` and run the k3s server install using `agents/deployer/manifests/bootstrap/setup-cluster.sh server`.
3. Run `setup-namespaces` and `setup-storage` on the new cluster.
4. Apply RBAC: copy `agents/deployer/manifests/rbac/agent-rbac.yaml` to the node and apply.
5. Run `bin/cluster-bootstrap` on the node to set up the readonly kubeconfig.
6. Add a new cluster entry to `~/.claude/profile/config.yaml` with the detected IPs and empty services.
7. Commit and push the config change.

## Notes

- All SSH operations use the deployer's auth flow (copy `profile/secrets/deployer`, run commands, clean up).
- These operations require the deployer agent's kubectl write authorization.
- `setup-cluster.sh` at `agents/deployer/manifests/bootstrap/setup-cluster.sh` contains the k3s server/agent install logic (used by `add-cluster` and `add-node`).
- After adding a cluster, the gateway and master stacks must be deployed separately.
- All subcommands are idempotent — safe to re-run on an already-configured cluster.
