---
name: add-node
description: Remotely add a worker node to an existing k3s cluster — installs Tailscale, joins via k3s agent over DERP relay, updates config.
argument-hint: "<ssh-target> [cluster]"
curated: true
scope: global
---

`/add-node <ssh-target> [cluster]`

Remotely provisions a machine and either joins it to an existing k3s cluster as a worker node, or bootstraps a new cluster with it as the control plane. All k3s traffic flows through Tailscale's DERP relay over port 443, so no direct 6443 access is needed between nodes.

Replaces the old `kordinate-cli join` command which required running on the node itself.

## Usage

```
/add-node kkord@10.95.43.74                    # interactive — prompts for cluster selection
/add-node kkord@10.95.43.74 homelab            # join existing cluster
/add-node kkord@192.168.1.50 staging --password
```

## Inputs

| Parameter | Required | Description |
|-----------|----------|-------------|
| `ssh-target` | yes | SSH connection string (e.g. `kkord@10.95.43.74`) |
| `cluster` | no | Cluster name — if omitted or not found, prompts user to choose |
| `--password` | no | Use password-based SSH via `sshpass` instead of key-based auth |

## Procedure

Authenticate before starting: use `/authenticate`.

### 1. Read config and resolve cluster

1. Parse `ssh-target` (and `cluster` if provided) from arguments
2. Read `profile/config.yaml` — collect all entries under `clusters`
3. **If a cluster name was provided:**
   - Look up `clusters.<cluster>`
   - If found → proceed to step 2 (join existing cluster path)
   - If NOT found → tell the user that cluster `<name>` doesn't exist, then fall through to the prompt below
4. **If no cluster name was provided, or the provided name was not found:**
   - List all available clusters by name
   - Present a numbered menu to the user:
     ```
     Available clusters:
       1. homelab
       2. staging
       3. Create new cluster

     Which cluster should this node join?
     ```
   - Wait for the user's response
   - If the user picks an existing cluster → proceed to step 2
   - If the user picks "Create new cluster" → ask for a cluster name, then proceed to step 2a (new cluster path)

---

### Path A: Join existing cluster (steps 2–8)

### 2. Validate cluster config

1. Confirm the selected cluster has a control plane entry with a Tailscale IP
2. Extract the control plane's Tailscale IP (`clusters.<cluster>.tailscale_ip`) and SSH target (`clusters.<cluster>.control_plane`)

### 3. Establish SSH connectivity

1. Test SSH to the target machine:
   - Key-based (default): `ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new <ssh-target> "echo ok"`
   - Password-based (`--password`): prompt for the password, then use `sshpass -p <password> ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new <ssh-target> "echo ok"`
2. If SSH fails, abort with a clear error message
3. Store the SSH prefix (with or without `sshpass`) for reuse in subsequent steps

### 4. Detect target architecture

1. Run on the target:
   ```
   ssh <ssh-target> "uname -m"
   ```
2. Map the result:
   - `x86_64` -> `amd64`
   - `aarch64` -> `arm64`
3. Store for use in binary downloads

### 5. Install Tailscale

1. Check if Tailscale is already installed:
   ```
   ssh <ssh-target> "command -v tailscale"
   ```
2. If not installed, install it:
   ```
   ssh <ssh-target> "curl -fsSL https://tailscale.com/install.sh | sudo sh"
   ```
3. Check if Tailscale is already authenticated:
   ```
   ssh <ssh-target> "sudo tailscale status --json 2>/dev/null | grep -q '\"BackendState\":\"Running\"'"
   ```
4. If not authenticated:
   - Try pre-auth key from pass store: `pass show kordinate/tailscale/preauth_key`
   - If a pre-auth key is available:
     ```
     ssh <ssh-target> "sudo tailscale up --authkey=<preauth-key>"
     ```
   - If no pre-auth key, start interactive auth and output the URL:
     ```
     ssh <ssh-target> "sudo tailscale up"
     ```
     The command will print a URL. Present it to the user and wait for them to confirm authentication is complete.
5. Verify Tailscale is connected:
   ```
   ssh <ssh-target> "tailscale status --self --json | grep -q '\"Online\":true'"
   ```
6. Capture the node's Tailscale IP for later use:
   ```
   ssh <ssh-target> "tailscale ip -4"
   ```

### 6. Fetch node token from control plane

The deployer already has Tailscale access to the control plane.

1. SSH to the control plane and retrieve the node token:
   ```
   ssh <control-plane-ssh> "sudo cat /var/lib/rancher/k3s/server/node-token"
   ```
   Where `<control-plane-ssh>` is the control plane's SSH target from config.yaml.
2. Store the token for the next step

### 7. Install k3s agent

1. Detect the node's hostname and LAN IP on the target:
   ```
   ssh <ssh-target> "hostname -s"
   ssh <ssh-target> "ip -4 route get 1.1.1.1 | awk '{print \$7; exit}'"
   ```
2. Get the node's Tailscale IP (captured in step 5.6)
3. Install k3s agent, pointing at the control plane's **Tailscale IP**:
   ```
   ssh <ssh-target> "curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC='agent' sh -s - \
       --server 'https://<control-plane-tailscale-ip>:6443' \
       --token '<node-token>' \
       --node-ip '<node-tailscale-ip>' \
       --node-name '<hostname>' \
       --flannel-iface tailscale0"
   ```
   Key flags:
   - `--server` uses the control plane's Tailscale IP so traffic routes through DERP on port 443
   - `--node-ip` is the node's own Tailscale IP so the cluster sees it on the Tailscale network
   - `--flannel-iface tailscale0` ensures flannel uses the Tailscale interface for pod networking
4. Wait for the k3s-agent service to start:
   ```
   ssh <ssh-target> "sudo systemctl is-active k3s-agent --wait"
   ```

### 8. Update config and verify

1. Read `profile/config.yaml`
2. Add the new node to `clusters.<cluster>.nodes`:
   ```yaml
   - name: <hostname>
     ip: <lan-ip>
     tailscale_ip: <tailscale-ip>
     role: agent
     arch: <amd64|arm64>
   ```
3. Write the updated config.yaml
4. SSH to the control plane and verify:
   ```
   ssh <control-plane-ssh> "kubectl wait --for=condition=Ready node/<hostname> --timeout=60s"
   ssh <control-plane-ssh> "kubectl get nodes"
   ```
5. If the node does not appear after 60 seconds, report the failure and suggest checking:
   - `ssh <ssh-target> "sudo journalctl -u k3s-agent --no-pager -n 50"` for agent logs
   - `ssh <ssh-target> "tailscale ping <control-plane-tailscale-ip>"` for Tailscale connectivity

---

### Path B: Create new cluster (steps 2a–8a)

This path bootstraps a new k3s cluster with the target node as the control plane, then deploys the full infrastructure stack.

### 2a. Establish SSH + detect architecture + install Tailscale

Same as steps 3, 4, and 5 from Path A. The node needs SSH access, architecture detection, and Tailscale before anything else.

### 3a. Install k3s server

1. Detect the node's hostname, LAN IP, and Tailscale IP (from step 2a)
2. Install k3s server remotely:
   ```
   ssh <ssh-target> "curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC='server' sh -s - \
       --node-ip '<node-tailscale-ip>' \
       --node-name '<hostname>' \
       --flannel-backend host-gw \
       --disable traefik \
       --disable servicelb \
       --write-kubeconfig-mode 644 \
       --kube-apiserver-arg service-node-port-range=8000-40000 \
       --kubelet-arg sync-frequency=1s \
       --flannel-iface tailscale0"
   ```
   These flags match `setup-cluster.sh` server mode, plus `--flannel-iface tailscale0` for Tailscale networking.
3. Wait for the k3s service to start:
   ```
   ssh <ssh-target> "sudo systemctl is-active k3s --wait"
   ```
4. Verify the node is Ready:
   ```
   ssh <ssh-target> "kubectl wait --for=condition=Ready node/<hostname> --timeout=60s"
   ```

### 4a. Add cluster to config.yaml

1. Read `profile/config.yaml`
2. Add a new entry under `clusters.<cluster-name>`:
   ```yaml
   <cluster-name>:
     name: <cluster-name>
     description: ""
     tailscale_ip: <node-tailscale-ip>
     gateway_tailscale_ip: <node-tailscale-ip>
     control_plane: <ssh-target>
     nodes:
       - name: <hostname>
         ip: <lan-ip>
         tailscale_ip: <node-tailscale-ip>
         role: server
         arch: <amd64|arm64>
     namespaces:
       - master
       - monitor
     services:
       registry:
         url: ""
   ```
3. Write the updated config.yaml
4. Ask the user to fill in any missing values (registry URL, description) later

### 5a. Deploy infrastructure

Run the standard cluster bootstrap sequence. Each step is idempotent:

1. **Setup namespaces and RBAC:**
   Apply `manifests/namespaces.yaml` and `manifests/agent-rbac.yaml` via SSH to the control plane.

2. **Setup storage (Longhorn):**
   Install `open-iscsi` on the node, install Longhorn, wait for rollout. See `deploy-cluster.md` → `setup-storage`.

3. **Generate overlays:**
   Run `/infra generate-overlays <cluster-name>` to produce the kustomize overlay directory at `profile/overlays/<cluster-name>/`.

4. **Setup secrets:**
   Create Kubernetes Secrets from `pass` store entries. See `deploy-cluster.md` → Secrets.

5. **Deploy monitor stack:**
   Apply monitor-namespace resources (Prometheus, Loki, Alloy, node-exporter, kube-state-metrics) via kustomize overlay.

6. **Deploy master stack:**
   Run the `deploy-master` procedure — kord-storage, workstation, Grafana, master Alloy, dashboards. See `deploy-cluster.md` → `deploy-master`.

### 6a. Final verification

1. Check all namespaces exist: `kubectl get namespaces`
2. Check all pods are running: `kubectl get pods -A`
3. Check storage is ready: `kubectl get sc longhorn`

---

## Report

- SSH connectivity method used (key-based or password)
- Target architecture detected
- Tailscale auth method used (pre-auth key or manual URL)
- Node Tailscale IP assigned
- Path taken: joined existing cluster OR created new cluster
- **If joined existing:** k3s agent install result, config.yaml updated, kubectl get nodes output
- **If created new:** k3s server install result, config.yaml updated, infrastructure deployment status (namespaces, storage, monitor, master)

## Notes

- All SSH operations use deployer auth flow
- This skill is idempotent: re-running on an already-joined node will detect existing Tailscale and k3s installations and skip those steps
- The k3s agent/server connects via Tailscale IP, not the LAN IP, so nodes can be on different networks
- DERP relay handles NAT traversal — no port forwarding or firewall rules needed for 6443
- If `sshpass` is needed but not installed locally, install it: `sudo apt-get install -y sshpass`
- The "create new cluster" path deploys the full infrastructure stack — this can take several minutes
- After creating a new cluster, deploy the gateway stack separately if the cluster needs to federate metrics to master
