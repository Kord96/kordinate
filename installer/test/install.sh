#!/usr/bin/env bash
set -euo pipefail

# Kordinate Installer — test version
# Uses k3d (k3s in docker) to avoid conflicts with existing k3s agent

CLUSTER_NAME="kordinate-test"
NAMESPACE="kordinate"
WORKSTATION_NAME="workstation-test"

log() { echo "[kordinate] $*"; }
err() { echo "[kordinate] ERROR: $*" >&2; exit 1; }

# --- Step 1: Create k3d cluster ---
log "Creating k3d cluster..."
if k3d cluster list 2>/dev/null | grep -q "$CLUSTER_NAME"; then
    log "Cluster $CLUSTER_NAME already exists, deleting..."
    k3d cluster delete "$CLUSTER_NAME"
fi
k3d cluster create "$CLUSTER_NAME" \
    --port "8080:8080@server:0" \
    --port "2222:22@server:0" \
    --wait

KUBECTL="k3d kubeconfig get $CLUSTER_NAME | kubectl --kubeconfig /dev/stdin"
# Simpler: merge kubeconfig
k3d kubeconfig merge "$CLUSTER_NAME" --kubeconfig-merge-default
KUBECTL="kubectl --context k3d-$CLUSTER_NAME"

log "k3s is ready"

# --- Step 2: Create namespace ---
log "Creating namespace $NAMESPACE..."
$KUBECTL create namespace "$NAMESPACE" --dry-run=client -o yaml | $KUBECTL apply -f -

# --- Step 3: Deploy headscale ---
log "Deploying headscale..."
$KUBECTL apply -n "$NAMESPACE" -f - <<'HEADSCALE_YAML'
apiVersion: v1
kind: ConfigMap
metadata:
  name: headscale-config
data:
  config.yaml: |
    server_url: http://headscale:8080
    listen_addr: 0.0.0.0:8080
    metrics_listen_addr: 0.0.0.0:9090
    private_key_path: /var/lib/headscale/private.key
    noise:
      private_key_path: /var/lib/headscale/noise_private.key
    database:
      type: sqlite
      sqlite:
        path: /var/lib/headscale/db.sqlite
    prefixes:
      v4: 100.64.0.0/10
      v6: fd7a:115c:a1e0::/48
    derp:
      server:
        enabled: true
        private_key_path: /var/lib/headscale/derp_server_private.key
        stun_listen_addr: 0.0.0.0:3478
      urls:
        - https://controlplane.tailscale.com/derpmap/default
    dns:
      magic_dns: true
      base_domain: kordinate.local
      nameservers:
        global:
          - 8.8.8.8
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: headscale
spec:
  replicas: 1
  selector:
    matchLabels:
      app: headscale
  template:
    metadata:
      labels:
        app: headscale
    spec:
      containers:
        - name: headscale
          image: headscale/headscale:0.25.1
          command: ["headscale", "serve"]
          ports:
            - containerPort: 8080
            - containerPort: 3478
              protocol: UDP
          volumeMounts:
            - name: config
              mountPath: /etc/headscale/config.yaml
              subPath: config.yaml
            - name: data
              mountPath: /var/lib/headscale
      volumes:
        - name: config
          configMap:
            name: headscale-config
        - name: data
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: headscale
spec:
  selector:
    app: headscale
  ports:
    - name: http
      port: 8080
      targetPort: 8080
    - name: stun
      port: 3478
      targetPort: 3478
      protocol: UDP
HEADSCALE_YAML

log "Waiting for headscale to be ready..."
$KUBECTL wait -n "$NAMESPACE" --for=condition=ready pod -l app=headscale --timeout=120s
sleep 5  # give headscale time to fully initialize

# --- Step 4: Create headscale user and auth key ---
log "Creating headscale user and auth key..."
HEADSCALE_POD=$($KUBECTL get pod -n "$NAMESPACE" -l app=headscale -o jsonpath='{.items[0].metadata.name}')

# Retry loop — headscale might not be fully ready
for i in 1 2 3 4 5; do
    if $KUBECTL exec -n "$NAMESPACE" "$HEADSCALE_POD" -- headscale users create kordinate 2>/dev/null; then
        break
    elif $KUBECTL exec -n "$NAMESPACE" "$HEADSCALE_POD" -- headscale users list 2>/dev/null | grep -q kordinate; then
        break
    fi
    log "Headscale not ready yet, retrying ($i/5)..."
    sleep 3
done

AUTH_KEY=$($KUBECTL exec -n "$NAMESPACE" "$HEADSCALE_POD" -- headscale preauthkeys create --user kordinate --reusable --expiration 24h -o json | python3 -c "import sys,json; print(json.load(sys.stdin)['key'])")
log "Auth key created"

# --- Step 5: Get headscale in-cluster URL ---
HEADSCALE_URL="http://headscale.${NAMESPACE}.svc.cluster.local:8080"
log "Headscale URL (in-cluster): $HEADSCALE_URL"

# --- Step 6: Deploy workstation ---
log "Deploying workstation..."
$KUBECTL apply -n "$NAMESPACE" -f - <<WORKSTATION_YAML
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $WORKSTATION_NAME
spec:
  replicas: 1
  selector:
    matchLabels:
      app: $WORKSTATION_NAME
  template:
    metadata:
      labels:
        app: $WORKSTATION_NAME
    spec:
      containers:
        - name: workstation
          image: ubuntu:24.04
          command: ["/bin/bash", "-c"]
          args:
            - |
              set -e
              export DEBIAN_FRONTEND=noninteractive
              apt-get update -qq
              apt-get install -y -qq openssh-server curl sudo iptables > /dev/null 2>&1

              # Create claude user
              useradd -m -s /bin/bash claude 2>/dev/null || true
              echo "claude ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/claude
              mkdir -p /home/claude/.ssh
              chmod 700 /home/claude/.ssh
              chown -R claude:claude /home/claude/.ssh

              # Install tailscale
              curl -fsSL https://tailscale.com/install.sh | sh
              tailscaled --state=/var/lib/tailscale/tailscaled.state &
              sleep 3
              tailscale up --login-server=$HEADSCALE_URL --authkey=$AUTH_KEY --hostname=$WORKSTATION_NAME

              # Start SSH
              mkdir -p /run/sshd
              ssh-keygen -A
              echo "SSH ready on tailscale hostname: $WORKSTATION_NAME"
              /usr/sbin/sshd -D
          securityContext:
            privileged: true
          ports:
            - containerPort: 22
---
apiVersion: v1
kind: Service
metadata:
  name: $WORKSTATION_NAME
spec:
  selector:
    app: $WORKSTATION_NAME
  ports:
    - port: 22
      targetPort: 22
WORKSTATION_YAML

log "Waiting for workstation to be ready (this may take a few minutes — installing packages)..."
$KUBECTL wait -n "$NAMESPACE" --for=condition=ready pod -l app=$WORKSTATION_NAME --timeout=300s
log "Workstation pod is running"

# Wait for tailscale + SSH inside the pod
log "Waiting for workstation to finish setup..."
sleep 15

# Check workstation tailscale status
WS_POD=$($KUBECTL get pod -n "$NAMESPACE" -l app=$WORKSTATION_NAME -o jsonpath='{.items[0].metadata.name}')
$KUBECTL logs -n "$NAMESPACE" "$WS_POD" --tail=5

log ""
log "=== Kordinate test install complete ==="
log ""
log "Connect via kubectl:"
log "  $KUBECTL exec -n $NAMESPACE -it $WS_POD -- su - claude"
log ""
log "Headscale nodes:"
$KUBECTL exec -n "$NAMESPACE" "$HEADSCALE_POD" -- headscale nodes list 2>/dev/null || true
log ""
log "To clean up:"
log "  k3d cluster delete $CLUSTER_NAME"
