# bootstrap

Manage cluster infrastructure: add nodes, add clusters, deploy gateway/master stacks.

## Arguments

`$ARGUMENTS` — Required format: `<subcommand> [args]`

## Subcommands

### add-node `<cluster> <node-ip>`

Add a worker node to an existing cluster.

1. Parse cluster name and node IP from `$ARGUMENTS`.
2. Read `~/.claude/config.yaml` to get the cluster's control plane IP and node token.
3. SSH to `<node-ip>` and run the k3s agent install:
   ```
   ssh <node-ip> "curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC=agent sh -s - \
     --server https://<control-plane-ip>:6443 --token <token> \
     --node-ip <node-ip> --node-name <hostname>"
   ```
4. Wait for the node to appear: `kubectl get nodes` (via SSH to control plane).
5. Update `~/.claude/config.yaml` — append the new IP to the cluster's `nodes` list.
6. Commit and push the config change.

### add-cluster `<name> <node-ip>`

Bootstrap a new k3s cluster on a remote machine.

1. Parse cluster name and node IP from `$ARGUMENTS`.
2. SSH to `<node-ip>` and run the k3s server install using `agents/deployer/manifests/bootstrap/setup-cluster.sh server`.
3. Run post-install (namespaces + Longhorn) via `setup-cluster.sh post-install`.
4. Apply RBAC: copy `agents/deployer/manifests/rbac/agent-rbac.yaml` to the node and apply.
5. Run `bin/cluster-bootstrap` on the node to set up the readonly kubeconfig.
6. Add a new cluster entry to `~/.claude/config.yaml` with the detected IPs and empty services.
7. Commit and push the config change.

### deploy-gateway `<cluster>`

Deploy the observability gateway stack to a cluster.

1. Parse cluster name from `$ARGUMENTS`.
2. Read `~/.claude/config.yaml` to get the cluster's Tailscale IP.
3. Check for a matching overlay in `agents/deployer/manifests/gateway/overlays/<cluster>/`. If none exists, create one from the template (patch cluster name and Tailscale hostname).
4. Prompt for Tailscale auth key (or read from `pass show kordinate/tailscale/auth_key_gateway`).
5. SSH to the cluster node:
   - Create the `gateway` namespace (if not exists).
   - Create the `tailscale-auth` secret with the auth key.
   - Copy gateway manifests (base + overlay) to the node.
   - Apply via `kubectl apply -k <overlay-dir>`.
6. Verify gateway pod is running.

### deploy-master `<cluster>`

Deploy master namespace manifests (Grafana, workstation, master gateway) to a cluster.

1. Parse cluster name from `$ARGUMENTS`.
2. Read `~/.claude/config.yaml` to get the cluster's Tailscale IP.
3. SSH to the cluster node:
   - Ensure `master` namespace exists.
   - Copy master manifests to the node.
   - Apply via `kubectl apply -k <base-dir>`.
4. Verify pods are running.

## Notes

- All SSH operations use the deployer's auth flow (copy `.deployer-secret`, run commands, clean up).
- These operations require the deployer agent's kubectl write authorization.
- `setup-cluster.sh` at `agents/deployer/manifests/bootstrap/setup-cluster.sh` contains the k3s install logic.
- After adding a cluster, the gateway and master stacks must be deployed separately.
