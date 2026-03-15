#!/usr/bin/env bash
set -euo pipefail

# Generic k3s cluster bootstrap script
# Supports: server, agent, agent-tainted, post-install

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()  { echo -e "${GREEN}[+]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*" >&2; }
info() { echo -e "${BLUE}[i]${NC} $*"; }

get_node_name() {
    local name
    name=$(hostname -s 2>/dev/null || true)
    if [[ -z "$name" || "$name" == "localhost" ]]; then
        local ip
        ip=$(get_node_ip)
        name="node-${ip##*.}"
        warn "Could not determine hostname, using $name"
    fi
    echo "$name"
}

get_node_ip() {
    if [[ -n "${NODE_IP:-}" ]]; then
        echo "$NODE_IP"
        return
    fi
    local ip
    ip=$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}')
    if [[ -z "$ip" ]]; then
        ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    fi
    if [[ -z "$ip" ]]; then
        err "Could not detect node IP. Set NODE_IP env var manually."
        exit 1
    fi
    echo "$ip"
}

install_server() {
    local node_ip node_name
    node_ip=$(get_node_ip)
    node_name=$(get_node_name)

    log "Installing k3s server"
    info "Node IP:   $node_ip"
    info "Node name: $node_name"
    echo

    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server" sh -s - \
        --node-ip "$node_ip" \
        --node-name "$node_name" \
        --flannel-backend host-gw \
        --disable traefik \
        --disable servicelb \
        --write-kubeconfig-mode 644 \
        --kube-apiserver-arg service-node-port-range=8000-40000

    log "k3s server installed"
    info "Kubeconfig: /etc/rancher/k3s/k3s.yaml"
    info "Node token: $(sudo cat /var/lib/rancher/k3s/server/node-token)"
    echo
    log "To add agents, run on each worker node:"
    echo "  $0 agent $node_ip"
}

install_agent() {
    local server_ip="$1"
    local node_ip node_name token

    node_ip=$(get_node_ip)
    node_name=$(get_node_name)

    echo -n "Enter node token from server: "
    read -r token

    log "Installing k3s agent"
    info "Server:    $server_ip"
    info "Node IP:   $node_ip"
    info "Node name: $node_name"
    echo

    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="agent" sh -s - \
        --server "https://${server_ip}:6443" \
        --token "$token" \
        --node-ip "$node_ip" \
        --node-name "$node_name"

    log "k3s agent installed and joined cluster"
}

install_agent_tainted() {
    local server_ip="$1"
    local node_ip node_name token

    node_ip=$(get_node_ip)
    node_name=$(get_node_name)

    echo -n "Enter node token from server: "
    read -r token

    log "Installing k3s tainted agent (PreferNoSchedule)"
    info "Server:    $server_ip"
    info "Node IP:   $node_ip"
    info "Node name: $node_name"
    echo

    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="agent" sh -s - \
        --server "https://${server_ip}:6443" \
        --token "$token" \
        --node-ip "$node_ip" \
        --node-name "$node_name" \
        --node-taint "node-role.kubernetes.io/overflow=true:PreferNoSchedule"

    log "k3s tainted agent installed and joined cluster"
}

post_install() {
    log "Running post-install configuration"

    # Check kubectl access
    if ! kubectl get nodes &>/dev/null; then
        err "Cannot reach cluster. Is kubeconfig set?"
        exit 1
    fi

    kubectl get nodes
    echo

    info "Current nodes:"
    kubectl get nodes -o wide
    echo

    # Create namespaces
    log "Creating namespaces"
    local SCRIPT_DIR
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ -f "$SCRIPT_DIR/namespaces.yaml" ]]; then
        kubectl apply -f "$SCRIPT_DIR/namespaces.yaml"
    else
        for ns in monitor test prod; do
            kubectl create namespace "$ns" --dry-run=client -o yaml | kubectl apply -f -
        done
    fi

    # Install Longhorn
    log "Installing Longhorn v1.7.3"
    kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.7.3/deploy/longhorn.yaml

    info "Waiting for Longhorn to be ready..."
    kubectl -n longhorn-system rollout status deploy/longhorn-driver-deployer --timeout=300s
    kubectl -n longhorn-system rollout status deploy/longhorn-ui --timeout=300s

    # Apply StorageClass from platform/base if available
    local MANIFESTS_ROOT
    MANIFESTS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
    if [[ -f "$MANIFESTS_ROOT/platform/base/storage.yaml" ]]; then
        log "Applying StorageClass"
        kubectl apply -f "$MANIFESTS_ROOT/platform/base/storage.yaml"
    else
        warn "No storage.yaml found at $MANIFESTS_ROOT/platform/base/storage.yaml -- apply manually"
    fi

    echo
    log "Post-install complete"
    info "Namespaces: monitor, test, prod"
    info "Longhorn: v1.7.3 installed"
    info "StorageClass: longhorn (reclaimPolicy=Retain)"
}

usage() {
    echo "Usage: $0 <command> [args]"
    echo
    echo "Commands:"
    echo "  server                Install k3s server node"
    echo "  agent <server-ip>     Install k3s agent and join cluster"
    echo "  agent-tainted <ip>    Install tainted agent (PreferNoSchedule)"
    echo "  post-install          Label nodes, install Longhorn, create namespaces"
    echo
    echo "Environment variables:"
    echo "  NODE_IP   Override auto-detected node IP"
}

case "${1:-}" in
    server)
        install_server
        ;;
    agent)
        [[ -z "${2:-}" ]] && { err "Usage: $0 agent <server-ip>"; exit 1; }
        install_agent "$2"
        ;;
    agent-tainted)
        [[ -z "${2:-}" ]] && { err "Usage: $0 agent-tainted <server-ip>"; exit 1; }
        install_agent_tainted "$2"
        ;;
    post-install)
        post_install
        ;;
    *)
        usage
        exit 1
        ;;
esac
