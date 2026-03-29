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
        --kube-apiserver-arg service-node-port-range=8000-40000 \
        --kubelet-arg sync-frequency=1s

    log "k3s server installed"
    info "Kubeconfig: /etc/rancher/k3s/k3s.yaml"
    info "Node token: $(sudo cat /var/lib/rancher/k3s/server/node-token)"
    echo
    log "To add agents, run on each worker node:"
    echo "  $0 agent $node_ip"
}

install_tailscale() {
    local ts_key="${TS_AUTHKEY:-}"
    local ts_hostname="${TS_HOSTNAME:-k3s-worker-$(get_node_name)}"

    if [[ -z "$ts_key" ]]; then
        err "TS_AUTHKEY env var required (ephemeral pre-authorized key)"
        exit 1
    fi

    log "Installing Tailscale"
    if ! command -v tailscale &>/dev/null; then
        curl -fsSL https://tailscale.com/install.sh | sh
    else
        info "Tailscale already installed"
    fi

    sudo tailscaled --state=/var/lib/tailscale/tailscaled.state &>/dev/null &
    sleep 2

    sudo tailscale up --authkey="$ts_key" --hostname="$ts_hostname"
    local ts_ip
    ts_ip=$(tailscale ip -4)
    log "Tailscale up: $ts_ip (hostname: $ts_hostname)"
    echo "$ts_ip"
}

install_agent() {
    local server_ip="$1"
    local node_name token

    node_name=$(get_node_name)

    # Install Tailscale first — use tailnet IP as the node IP
    local ts_ip
    ts_ip=$(install_tailscale)

    if [[ -n "${K3S_TOKEN:-}" ]]; then
        token="$K3S_TOKEN"
    else
        echo -n "Enter node token from server: "
        read -r token
    fi

    log "Installing k3s agent"
    info "Server:    $server_ip (control plane tailscale IP)"
    info "Node IP:   $ts_ip (tailscale)"
    info "Node name: $node_name"
    echo

    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="agent" sh -s - \
        --server "https://${server_ip}:6443" \
        --token "$token" \
        --node-ip "$ts_ip" \
        --node-name "$node_name"

    log "k3s agent installed and joined cluster via tailnet"
}

install_agent_tainted() {
    local server_ip="$1"
    local node_name token

    node_name=$(get_node_name)

    # Install Tailscale first — use tailnet IP as the node IP
    local ts_ip
    ts_ip=$(install_tailscale)

    if [[ -n "${K3S_TOKEN:-}" ]]; then
        token="$K3S_TOKEN"
    else
        echo -n "Enter node token from server: "
        read -r token
    fi

    log "Installing k3s tainted agent (PreferNoSchedule)"
    info "Server:    $server_ip (control plane tailscale IP)"
    info "Node IP:   $ts_ip (tailscale)"
    info "Node name: $node_name"
    echo

    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="agent" sh -s - \
        --server "https://${server_ip}:6443" \
        --token "$token" \
        --node-ip "$ts_ip" \
        --node-name "$node_name" \
        --node-taint "node-role.kubernetes.io/overflow=true:PreferNoSchedule"

    log "k3s tainted agent installed and joined cluster via tailnet"
}

## post-install is handled by the charon agent:
##   /charon:bootstrap setup-namespaces
##   /charon:bootstrap setup-storage

usage() {
    echo "Usage: $0 <command> [args]"
    echo
    echo "Commands:"
    echo "  server                Install k3s server node"
    echo "  agent <server-ip>     Install k3s agent and join cluster"
    echo "  agent-tainted <ip>    Install tainted agent (PreferNoSchedule)"
    echo "  (post-install is handled by charon: /charon:bootstrap setup-namespaces + setup-storage)"
    echo
    echo "Environment variables:"
    echo "  TS_AUTHKEY    Tailscale ephemeral pre-auth key (required for agent/agent-tainted)"
    echo "  TS_HOSTNAME   Override Tailscale hostname (default: k3s-worker-<hostname>)"
    echo "  K3S_TOKEN     k3s node token (avoids interactive prompt)"
    echo "  NODE_IP       Override auto-detected node IP (server mode only)"
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
        echo "post-install is now handled by the charon agent."
        echo "Use: /charon:bootstrap setup-namespaces"
        echo "     /charon:bootstrap setup-storage"
        exit 1
        ;;
    *)
        usage
        exit 1
        ;;
esac
