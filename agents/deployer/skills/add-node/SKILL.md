---
name: add-node
description: Remotely add a worker node to an existing k3s cluster — installs Tailscale, joins via k3s agent over DERP relay, updates config.
argument-hint: "<ssh-target> <cluster>"
curated: true
scope: global
---

`/add-node <ssh-target> <cluster>`

Remotely provisions a machine and joins it to an existing k3s cluster as a worker node. All k3s agent traffic flows through Tailscale's DERP relay over port 443, so no direct 6443 access is needed between nodes.

Replaces the old `kordinate-cli join` command which required running on the node itself.

## Usage

```
/add-node kkord@10.95.43.74 homelab
/add-node kkord@192.168.1.50 staging --password
```

## Inputs

| Parameter | Required | Description |
|-----------|----------|-------------|
| `ssh-target` | yes | SSH connection string (e.g. `kkord@10.95.43.74`) |
| `cluster` | yes | Cluster name as defined in `profile/config.yaml` |
| `--password` | no | Use password-based SSH via `sshpass` instead of key-based auth |

## Procedure

Authenticate before starting: use `/authenticate`.

### 1. Validate inputs

1. Parse `ssh-target` and `cluster` from arguments
2. Read `profile/config.yaml` — look up `clusters.<cluster>`
3. Confirm the cluster exists and has a control plane entry with a Tailscale IP
4. Extract the control plane's Tailscale IP (`clusters.<cluster>.tailscale_ip`) and SSH target (`clusters.<cluster>.control_plane`)

### 2. Establish SSH connectivity

1. Test SSH to the target machine:
   - Key-based (default): `ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new <ssh-target> "echo ok"`
   - Password-based (`--password`): prompt for the password, then use `sshpass -p <password> ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new <ssh-target> "echo ok"`
2. If SSH fails, abort with a clear error message
3. Store the SSH prefix (with or without `sshpass`) for reuse in subsequent steps

### 3. Detect target architecture

1. Run on the target:
   ```
   ssh <ssh-target> "uname -m"
   ```
2. Map the result:
   - `x86_64` -> `amd64`
   - `aarch64` -> `arm64`
3. Store for use in binary downloads

### 4. Install Tailscale

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

### 5. Fetch node token from control plane

The deployer already has Tailscale access to the control plane.

1. SSH to the control plane and retrieve the node token:
   ```
   ssh <control-plane-ssh> "sudo cat /var/lib/rancher/k3s/server/node-token"
   ```
   Where `<control-plane-ssh>` is the control plane's SSH target from config.yaml.
2. Store the token for the next step

### 6. Install k3s agent

1. Detect the node's hostname and LAN IP on the target:
   ```
   ssh <ssh-target> "hostname -s"
   ssh <ssh-target> "ip -4 route get 1.1.1.1 | awk '{print \$7; exit}'"
   ```
2. Get the node's Tailscale IP (captured in step 4.6)
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

### 7. Update config.yaml

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

### 8. Verify node joined

1. SSH to the control plane and check:
   ```
   ssh <control-plane-ssh> "kubectl get nodes"
   ```
2. Confirm the new node's hostname appears in the output with status `Ready` (may take up to 60 seconds):
   ```
   ssh <control-plane-ssh> "kubectl wait --for=condition=Ready node/<hostname> --timeout=60s"
   ```
3. If the node does not appear after 60 seconds, report the failure and suggest checking:
   - `ssh <ssh-target> "sudo journalctl -u k3s-agent --no-pager -n 50"` for agent logs
   - `ssh <ssh-target> "tailscale ping <control-plane-tailscale-ip>"` for Tailscale connectivity

Remove auth when done.

## Report

- SSH connectivity method used (key-based or password)
- Target architecture detected
- Tailscale auth method used (pre-auth key or manual URL)
- Node Tailscale IP assigned
- k3s agent install result
- config.yaml updated (new node entry)
- kubectl get nodes output showing the new node

## Notes

- All SSH operations use deployer auth flow
- This skill is idempotent: re-running on an already-joined node will detect existing Tailscale and k3s installations and skip those steps
- The k3s agent connects to the server's Tailscale IP, not the LAN IP, so nodes can be on different networks
- DERP relay handles NAT traversal — no port forwarding or firewall rules needed for 6443
- If `sshpass` is needed but not installed locally, install it: `sudo apt-get install -y sshpass`
