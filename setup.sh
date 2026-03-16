#!/bin/bash
# Kordinate setup — run on bare metal to bootstrap k3s and deploy the workstation pod.
#
# Usage:
#   sudo ./setup.sh          # install k3s (if needed), deploy workstation, setup auth
#   ./setup.sh hydrate        # generate .mcp.json from config.yaml + pass
#   ./setup.sh export         # bundle pass store → encrypted archive
#   ./setup.sh import         # restore pass store from encrypted archive
#
# Prerequisites: git, gh (authenticated), curl, python3.
# Runs locally — no SSH required.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/setup/lib.sh"

WORKSTATION_DIR="$SCRIPT_DIR/agents/deployer/manifests/master/base/workstation"
MANIFESTS="$SCRIPT_DIR/agents/deployer/manifests"

CMD="${1:-}"

# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

require_cmd() {
  if ! command -v "$1" &>/dev/null; then
    err "$1 is required. $2"
    exit 1
  fi
}

require_root() {
  if [ "$(id -u)" -ne 0 ]; then
    err "Setup must run as root. Run: sudo $0 $*"
    exit 1
  fi
}

# Read a value from config.yaml
read_config() {
  python3 -c "
import yaml, sys
c = yaml.safe_load(open('$SCRIPT_DIR/config.yaml'))
path = sys.argv[1].split('.')
v = c
for p in path:
    if isinstance(v, dict) and p in v:
        v = v[p]
    else:
        sys.exit(1)
print(v)
" "$1" 2>/dev/null
}

# Detect node IP (same logic as setup-cluster.sh)
detect_node_ip() {
  if [ -n "${NODE_IP:-}" ]; then
    echo "$NODE_IP"
    return
  fi
  local ip
  ip=$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}')
  if [ -z "$ip" ]; then
    ip=$(hostname -I 2>/dev/null | awk '{print $1}')
  fi
  if [ -z "$ip" ]; then
    err "Could not detect node IP. Set NODE_IP env var."
    exit 1
  fi
  echo "$ip"
}

# kubectl using the k3s admin kubeconfig
kc() {
  KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl "$@"
}

# kubectl exec into the workstation pod
ws_exec() {
  kc exec -n master deploy/workstation -c workstation -- bash -c "$*"
}

# Get workstation pod name
ws_pod() {
  kc get pod -n master -l component=workstation -o jsonpath='{.items[0].metadata.name}'
}

# ═══════════════════════════════════════════════════════════════
# MAIN SETUP — install k3s if needed, deploy workstation, auth
# ═══════════════════════════════════════════════════════════════
cmd_setup() {
  echo -e "${BOLD}kordinate setup${NC}"
  echo ""

  require_cmd git "apt install git"
  require_cmd curl "apt install curl"
  require_cmd python3 "apt install python3"
  require_root

  # ─── Step 1: Ensure k3s is running ───
  echo -e "${BOLD}Step 1: Kubernetes${NC}"

  if systemctl is-active --quiet k3s 2>/dev/null; then
    log "k3s already running"
    kc get nodes
  else
    info "k3s not found — installing..."
    local NODE_IP NODE_NAME
    NODE_IP=$(detect_node_ip)
    NODE_NAME=$(hostname -s)

    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server" sh -s - \
      --node-ip "$NODE_IP" \
      --node-name "$NODE_NAME" \
      --flannel-backend host-gw \
      --disable traefik \
      --disable servicelb \
      --write-kubeconfig-mode 644 \
      --kube-apiserver-arg service-node-port-range=8000-40000

    info "Waiting for node to be ready..."
    kc wait --for=condition=Ready node "$NODE_NAME" --timeout=120s
    log "k3s installed (node: $NODE_NAME, ip: $NODE_IP)"

    # Install Longhorn
    echo ""
    info "Installing Longhorn storage..."
    kc apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.7.3/deploy/longhorn.yaml
    info "Waiting for Longhorn (this takes a few minutes)..."
    kc -n longhorn-system rollout status deploy/longhorn-driver-deployer --timeout=300s
    kc -n longhorn-system rollout status deploy/longhorn-ui --timeout=300s
    log "Longhorn installed"
  fi

  # ─── Step 2: Namespaces + RBAC ───
  echo ""
  echo -e "${BOLD}Step 2: Namespaces & RBAC${NC}"

  kc apply -f "$MANIFESTS/bootstrap/namespaces.yaml"
  log "Namespaces ready"

  kc apply -f "$MANIFESTS/rbac/agent-rbac.yaml"
  log "RBAC applied"

  # ─── Step 3: Build workstation image ───
  echo ""
  echo -e "${BOLD}Step 3: Build workstation image${NC}"

  if ! command -v docker &>/dev/null; then
    info "Installing docker for image builds..."
    apt-get update -qq && apt-get install -y -qq docker.io >/dev/null
  fi

  info "Building image..."
  docker build -t local/workstation:latest "$WORKSTATION_DIR"
  docker save local/workstation:latest | k3s ctr images import -
  log "Image imported to k3s"

  # ─── Step 4: Deploy workstation ───
  echo ""
  echo -e "${BOLD}Step 4: Deploy workstation${NC}"

  local REPO_URL MANIFEST
  REPO_URL=$(git -C "$SCRIPT_DIR" remote get-url origin 2>/dev/null || true)

  MANIFEST=$(mktemp)
  sed \
    -e 's|image: REGISTRY/workstation:latest|image: local/workstation:latest|' \
    -e '/image: local\/workstation:latest/a\          imagePullPolicy: Never' \
    -e "s|MUST_BE_SET|${REPO_URL}|" \
    "$MANIFESTS/master/base/workstation.yaml" > "$MANIFEST"

  kc apply -f "$MANIFEST"
  rm -f "$MANIFEST"
  log "Workstation deployed"

  # ─── Step 5: Wait for pod ───
  echo ""
  echo -e "${BOLD}Step 5: Waiting for workstation pod${NC}"

  info "Waiting for pod to be ready..."
  kc -n master wait --for=condition=Ready pod -l component=workstation --timeout=180s
  log "Workstation pod running"

  # ─── Step 6: Link repo ───
  echo ""
  echo -e "${BOLD}Step 6: Link repo${NC}"

  if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
    read -rp "Remote repo URL for workstation ~/.claude (enter to auto-create): " LINK_REPO

    if [ -z "$LINK_REPO" ]; then
      info "No repo provided — creating private kordinate repo..."
      local GH_USER
      GH_USER=$(gh api user -q .login)
      local REPO_NAME="kordinate"

      if gh repo view "${GH_USER}/${REPO_NAME}" &>/dev/null 2>&1; then
        info "Repo ${GH_USER}/${REPO_NAME} already exists"
      else
        gh repo create "$REPO_NAME" --private --confirm
        log "Created private repo: ${GH_USER}/${REPO_NAME}"

        local TMP_REPO
        TMP_REPO=$(mktemp -d)
        git init "$TMP_REPO"
        cp -r "$SCRIPT_DIR/agents" "$SCRIPT_DIR/commands" "$SCRIPT_DIR/hooks" \
              "$SCRIPT_DIR/CLAUDE.md" "$SCRIPT_DIR/config.yaml.template" \
              "$SCRIPT_DIR/settings.json" "$SCRIPT_DIR/bin" "$SCRIPT_DIR/setup.sh" "$SCRIPT_DIR/setup" \
              "$TMP_REPO/" 2>/dev/null || true
        [ -f "$SCRIPT_DIR/config.yaml" ] && cp "$SCRIPT_DIR/config.yaml" "$TMP_REPO/"
        git -C "$TMP_REPO" add -A
        git -C "$TMP_REPO" commit -m "initial kordinate setup"
        git -C "$TMP_REPO" remote add origin "https://github.com/${GH_USER}/${REPO_NAME}.git"
        git -C "$TMP_REPO" push -u origin HEAD:main
        rm -rf "$TMP_REPO"
        log "Scaffolded data pushed to repo"
      fi

      LINK_REPO="https://github.com/${GH_USER}/${REPO_NAME}.git"
    fi

    ws_exec "git clone $LINK_REPO ~/.claude 2>/dev/null || git -C ~/.claude pull --ff-only"
    log "Linked workstation to $LINK_REPO"
  else
    warn "gh not authenticated — skipping repo link. Run gh auth login on the workstation later."
  fi

  # ─── Step 7: Credentials (optional) ───
  echo ""
  echo -e "${BOLD}Step 7: Credentials${NC}"

  read -rp "Path to GPG key export file (enter to skip): " GPG_KEY_PATH
  if [ -n "$GPG_KEY_PATH" ] && [ -f "$GPG_KEY_PATH" ]; then
    local POD
    POD=$(ws_pod)
    kc cp "$GPG_KEY_PATH" "master/$POD:/tmp/gpg-key.asc" -c workstation
    ws_exec "gpg --batch --import /tmp/gpg-key.asc && rm /tmp/gpg-key.asc"
    ws_exec 'GPG_KEY_ID=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep -m1 "^sec" | awk "{print \$2}" | cut -d/ -f2) && echo "${GPG_KEY_ID}:6:" | gpg --import-ownertrust'
    log "GPG key imported on workstation"

    if [ -d "$HOME/.password-store/kordinate" ]; then
      read -rp "Copy local pass store to workstation? [Y/n] " answer
      case "${answer:-y}" in
        [nN]*) ;;
        *)
          local TMP_PASS="/tmp/kordinate-pass.tar.gz"
          tar czf "$TMP_PASS" -C "$HOME" .password-store
          kc cp "$TMP_PASS" "master/$POD:/tmp/kordinate-pass.tar.gz" -c workstation
          ws_exec "cd /home/claude && tar xzf /tmp/kordinate-pass.tar.gz && rm /tmp/kordinate-pass.tar.gz"
          rm -f "$TMP_PASS"
          log "Pass store copied to workstation"
          ;;
      esac
    fi
  else
    info "No GPG key provided — auth-check will create fresh credentials"
  fi

  # ─── Step 8: Auth check ───
  echo ""
  echo -e "${BOLD}Step 8: Auth setup${NC}"

  local AUTH_SCRIPT="$SCRIPT_DIR/setup/auth-check.sh"
  if [ -f "$AUTH_SCRIPT" ]; then
    local POD
    POD=$(ws_pod)
    kc cp "$AUTH_SCRIPT" "master/$POD:/tmp/auth-check.sh" -c workstation
    kc exec -it -n master deploy/workstation -c workstation -- bash /tmp/auth-check.sh
  fi

  # ─── Step 9: Generate config.yaml if missing ───
  echo ""
  echo -e "${BOLD}Step 9: Config${NC}"

  if [ -f "$SCRIPT_DIR/config.yaml" ]; then
    log "config.yaml already exists"
  else
    local NODE_IP CLUSTER_NAME TS_IP
    NODE_IP=$(detect_node_ip)
    CLUSTER_NAME=$(hostname -s | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9-')
    TS_IP=$(tailscale ip -4 2>/dev/null || echo "")

    python3 -c "
import yaml
config = {
    'clusters': {
        '$CLUSTER_NAME': {
            'name': '$CLUSTER_NAME',
            'description': 'Single-node k3s cluster',
            'tailscale_ip': '$TS_IP' or None,
            'nodes': ['$NODE_IP'],
            'namespaces': ['gateway', 'master', 'dev', 'test', 'prod'],
            'manifests': {
                'master': 'agents/deployer/manifests/master',
                'gateway': 'agents/deployer/manifests/gateway',
                'bootstrap': 'agents/deployer/manifests/bootstrap',
            },
            'workloads': [],
            'services': {},
        }
    },
    'network': {'tailnet': '', 'grafana_public': ''},
    'cloudflare': {'account_id': '', 'tunnel_id': '', 'tunnel_name': '', 'domains': []},
}
with open('$SCRIPT_DIR/config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
"
    log "Generated config.yaml for cluster $CLUSTER_NAME"
  fi

  echo ""
  log "Setup complete!"
  echo ""
  echo "  Access workstation:"
  echo "    kubectl -n master exec -it deploy/workstation -c workstation -- bash"
  echo "    ssh workstation  (after Tailscale is configured)"
  echo ""
  echo "  Then run:  claude login"
}

# ═══════════════════════════════════════════════════════════════
# HYDRATE — generate .mcp.json from config.yaml + pass
# (runs on the workstation, not the host)
# ═══════════════════════════════════════════════════════════════
cmd_hydrate() {
  local CONFIG
  # Try workstation path first, fall back to script dir
  if [ -f "$HOME/.claude/config.yaml" ]; then
    CONFIG="$HOME/.claude/config.yaml"
  elif [ -f "$SCRIPT_DIR/config.yaml" ]; then
    CONFIG="$SCRIPT_DIR/config.yaml"
  else
    err "config.yaml not found"
    exit 1
  fi

  local OUTPUT_DIR
  if [ -d "$HOME/.claude" ]; then
    OUTPUT_DIR="$HOME/.claude"
  else
    OUTPUT_DIR="$SCRIPT_DIR"
  fi

  local GRAFANA_TOKEN
  GRAFANA_TOKEN=$(pass show kordinate/grafana_admin/api_key 2>/dev/null || echo "")

  echo "Generating .mcp.json..."

  python3 -c "
import yaml, json, sys

c = yaml.safe_load(open('$CONFIG'))
clusters = c.get('clusters', {})
grafana_token = '''$GRAFANA_TOKEN'''
grafana_added = False

mcp = {'mcpServers': {}}

for name, cl in clusters.items():
    ip = cl.get('tailscale_ip', '')
    if not ip or ip == '100.x.x.x':
        continue
    svcs = cl.get('services', {})

    # Postgres
    pg = svcs.get('postgres', {})
    if pg.get('port') and pg.get('user') and pg.get('database'):
        mcp['mcpServers'][f'postgres-{name}'] = {
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-postgres',
                     f\"postgresql://{pg['user']}@{ip}:{pg['port']}/{pg['database']}\"]
        }

    # Redis
    redis = svcs.get('redis', {})
    if redis.get('port'):
        mcp['mcpServers'][f'redis-{name}'] = {
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-redis'],
            'env': {
                'REDIS_HOST': ip,
                'REDIS_PORT': str(redis['port'])
            }
        }

    # Grafana (singleton — only add from the first cluster that has it)
    grafana = svcs.get('grafana', {})
    if grafana.get('port') and not grafana_added:
        env = {'GRAFANA_URL': f\"http://{ip}:{grafana['port']}\"}
        if grafana_token:
            env['GRAFANA_SERVICE_ACCOUNT_TOKEN'] = grafana_token
        mcp['mcpServers']['grafana-admin'] = {
            'command': 'uvx',
            'args': ['mcp-grafana'],
            'env': env
        }
        grafana_added = True

print(json.dumps(mcp, indent=2))
" > "$OUTPUT_DIR/.mcp.json"

  log "Generated .mcp.json at $OUTPUT_DIR/.mcp.json"
}

# ═══════════════════════════════════════════════════════════════
# EXPORT — bundle pass store → encrypted archive
# ═══════════════════════════════════════════════════════════════
cmd_export() {
  local OUTPUT="${1:-kordinate-export.gpg}"
  local WORK_DIR
  WORK_DIR="$(mktemp -d)"
  trap 'rm -rf "$WORK_DIR"' EXIT

  # Export GPG key
  echo "Exporting GPG key..."
  local GPG_KEY_ID
  GPG_KEY_ID=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep -m1 '^sec' | awk '{print $2}' | cut -d/ -f2 || true)
  if [ -n "$GPG_KEY_ID" ]; then
    gpg --export-secret-keys --armor "$GPG_KEY_ID" > "$WORK_DIR/gpg-key.asc"
    echo "  + gpg-key.asc"
  fi

  # Export pass store
  echo "Exporting pass store..."
  if [ -d "$HOME/.password-store/kordinate" ]; then
    cp -r "$HOME/.password-store" "$WORK_DIR/password-store"
    echo "  + password-store/"
  fi

  echo ""
  echo "Creating encrypted archive..."
  tar czf "$WORK_DIR/bundle.tar.gz" -C "$WORK_DIR" .
  gpg --batch --yes --symmetric --cipher-algo AES256 -o "$OUTPUT" "$WORK_DIR/bundle.tar.gz"

  echo ""
  log "Export complete: $OUTPUT"
}

# ═══════════════════════════════════════════════════════════════
# IMPORT — restore pass store from encrypted archive
# ═══════════════════════════════════════════════════════════════
cmd_import() {
  local ARCHIVE="${1:-}"
  if [ -z "$ARCHIVE" ] || [ ! -f "$ARCHIVE" ]; then
    err "Usage: ./setup.sh import <archive.gpg>"
    exit 1
  fi

  local WORK_DIR
  WORK_DIR="$(mktemp -d)"
  trap 'rm -rf "$WORK_DIR"' EXIT

  echo "Decrypting archive..."
  gpg --batch --yes -d "$ARCHIVE" | tar xzf - -C "$WORK_DIR"

  # Import GPG key
  if [ -f "$WORK_DIR/gpg-key.asc" ]; then
    gpg --batch --import "$WORK_DIR/gpg-key.asc"
    local GPG_KEY_ID
    GPG_KEY_ID=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep -m1 '^sec' | awk '{print $2}' | cut -d/ -f2)
    echo "${GPG_KEY_ID}:6:" | gpg --import-ownertrust
    log "GPG key imported: $GPG_KEY_ID"
  fi

  # Import pass store
  if [ -d "$WORK_DIR/password-store" ]; then
    cp -r "$WORK_DIR/password-store" "$HOME/.password-store"
    log "Pass store restored"
  fi

  echo ""
  log "Import complete."
}

# ═══════════════════════════════════════════════════════════════
# MAIN DISPATCHER
# ═══════════════════════════════════════════════════════════════
usage() {
  echo "Usage: sudo ./setup.sh [command]"
  echo ""
  echo "  (no args)     Install k3s (if needed), deploy workstation, setup auth"
  echo "  hydrate        Generate .mcp.json from config.yaml + pass"
  echo "  export         Bundle GPG key + pass store → encrypted archive"
  echo "  import         Restore GPG key + pass store from archive"
  echo ""
  echo "Run on the bare metal machine that will host the cluster."
  echo "Adding nodes/clusters is handled by the deployer agent."
}

case "${CMD:-setup}" in
  setup|"")  cmd_setup ;;
  hydrate)   cmd_hydrate ;;
  export)    cmd_export "${@:2}" ;;
  import)    cmd_import "${@:2}" ;;
  *) usage; exit 1 ;;
esac
