#!/bin/bash
# Kordinate setup — deploy a workstation pod to an existing k8s cluster.
#
# Usage:
#   ./setup.sh              # interactive: deploy workstation, link repo, setup auth
#   ./setup.sh bootstrap    # cluster infrastructure (k3s, gateway, RBAC)
#   ./setup.sh export       # bundle pass store → encrypted archive
#   ./setup.sh import       # restore pass store from encrypted archive
#
# Prerequisites: git, gh (authenticated), ssh access to cluster node.
# The workstation image has all other tools baked in.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/setup/lib.sh"

WORKSTATION_DIR="$SCRIPT_DIR/agents/deployer/manifests/master/base/workstation"
MASTER_MANIFESTS="$SCRIPT_DIR/agents/deployer/manifests/master"

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

# Run kubectl on a remote node via SSH
remote_kc() {
  local node="$1"; shift
  ssh "$node" "sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml $*"
}

# Run a command inside the workstation pod via kubectl exec
ws_exec() {
  local node="$1"; shift
  ssh "$node" "sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml exec -n master deploy/workstation -c workstation -- bash -c '$*'"
}

# ═══════════════════════════════════════════════════════════════
# MAIN SETUP — deploy workstation, link repo, setup auth
# ═══════════════════════════════════════════════════════════════
cmd_setup() {
  echo -e "${BOLD}kordinate setup${NC}"
  echo ""

  require_cmd git "apt install git"
  require_cmd gh "https://cli.github.com"
  require_cmd ssh "apt install openssh-client"
  require_cmd python3 "apt install python3"

  if ! gh auth status &>/dev/null 2>&1; then
    err "GitHub CLI not authenticated. Run: gh auth login"
    exit 1
  fi

  # ─── Step 1: Find the cluster ───
  echo -e "${BOLD}Step 1: Cluster${NC}"

  if [ ! -f "$SCRIPT_DIR/config.yaml" ]; then
    err "config.yaml not found. Copy config.yaml.template and fill in cluster IPs."
    exit 1
  fi

  local NODE
  NODE=$(read_config clusters.home.tailscale_ip 2>/dev/null || true)
  if [ -z "$NODE" ] || [ "$NODE" = "100.x.x.x" ]; then
    read -rp "Cluster node IP (Tailscale or LAN): " NODE
  fi

  if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$NODE" true &>/dev/null; then
    err "Cannot SSH to $NODE"
    exit 1
  fi
  log "Cluster reachable at $NODE"

  # ─── Step 2: Build and push workstation image ───
  echo ""
  echo -e "${BOLD}Step 2: Build workstation image${NC}"

  local REGISTRY
  REGISTRY=$(read_config clusters.home.services.registry.url 2>/dev/null || true)
  if [ -z "$REGISTRY" ]; then
    REGISTRY=$(read_config clusters.datacenter.services.registry.url 2>/dev/null || true)
  fi
  if [ -z "$REGISTRY" ]; then
    read -rp "Container registry (host:port): " REGISTRY
  fi

  info "Building workstation image on $NODE..."
  local BUILD_DIR="/tmp/kordinate-workstation-build"
  ssh "$NODE" "rm -rf $BUILD_DIR && mkdir -p $BUILD_DIR"
  scp -r "$WORKSTATION_DIR/Dockerfile" "$WORKSTATION_DIR/entrypoint.sh" "$NODE:$BUILD_DIR/"
  ssh "$NODE" "cd $BUILD_DIR && docker build -t $REGISTRY/workstation:latest . && docker push $REGISTRY/workstation:latest"
  log "Image pushed to $REGISTRY/workstation:latest"

  # ─── Step 3: Deploy workstation pod ───
  echo ""
  echo -e "${BOLD}Step 3: Deploy workstation${NC}"

  local REPO_URL
  REPO_URL=$(git -C "$SCRIPT_DIR" remote get-url origin 2>/dev/null || true)

  # Patch manifest with real values
  local MANIFEST
  MANIFEST=$(mktemp)
  sed \
    -e "s|REGISTRY/workstation:latest|$REGISTRY/workstation:latest|" \
    -e "s|MUST_BE_SET|$REPO_URL|" \
    "$SCRIPT_DIR/agents/deployer/manifests/master/base/workstation.yaml" > "$MANIFEST"

  local TMP_MANIFEST="/tmp/kordinate-workstation.yaml"
  scp "$MANIFEST" "$NODE:$TMP_MANIFEST"
  rm -f "$MANIFEST"

  remote_kc "$NODE" "create namespace master --dry-run=client -o yaml | sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml apply -f -"
  remote_kc "$NODE" "apply -f $TMP_MANIFEST"
  log "Workstation deployed"

  info "Waiting for workstation pod to be ready..."
  local attempts=0
  while ! remote_kc "$NODE" "get pod -n master -l component=workstation --no-headers 2>/dev/null" | grep -q Running; do
    ((attempts++))
    if [ "$attempts" -gt 60 ]; then
      err "Workstation pod not ready after 60s"
      exit 1
    fi
    sleep 2
  done
  log "Workstation pod running"

  # ─── Step 4: Link repo on workstation ───
  echo ""
  echo -e "${BOLD}Step 4: Link repo${NC}"

  read -rp "Remote repo URL for workstation ~/.claude: " LINK_REPO

  # If no repo provided, auto-create one
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

      # Push scaffolded data to it
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

  ws_exec "$NODE" "git clone $LINK_REPO ~/.claude 2>/dev/null || git -C ~/.claude pull --ff-only"
  log "Linked workstation to $LINK_REPO"

  # ─── Step 5: Copy GPG key + pass store (if available) ───
  echo ""
  echo -e "${BOLD}Step 5: Credentials${NC}"

  read -rp "Path to GPG key export file (enter to skip): " GPG_KEY_PATH
  if [ -n "$GPG_KEY_PATH" ] && [ -f "$GPG_KEY_PATH" ]; then
    local TMP_KEY="/tmp/kordinate-gpg-key.asc"
    scp "$GPG_KEY_PATH" "$NODE:$TMP_KEY"
    local POD
    POD=$(ssh "$NODE" "sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml get pod -n master -l component=workstation -o jsonpath='{.items[0].metadata.name}'")
    ssh "$NODE" "sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml cp $TMP_KEY master/$POD:/tmp/gpg-key.asc -c workstation"
    ws_exec "$NODE" "gpg --batch --import /tmp/gpg-key.asc && rm /tmp/gpg-key.asc"

    # Trust the key
    ws_exec "$NODE" "GPG_KEY_ID=\$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep -m1 '^sec' | awk '{print \$2}' | cut -d/ -f2) && echo \"\${GPG_KEY_ID}:6:\" | gpg --import-ownertrust"
    log "GPG key imported on workstation"

    # Copy pass store if available
    if [ -d "$HOME/.password-store/kordinate" ]; then
      read -rp "Copy local pass store to workstation? [Y/n] " answer
      case "${answer:-y}" in
        [nN]*) ;;
        *)
          local TMP_PASS="/tmp/kordinate-pass.tar.gz"
          tar czf "$TMP_PASS" -C "$HOME" .password-store
          scp "$TMP_PASS" "$NODE:/tmp/kordinate-pass.tar.gz"
          ssh "$NODE" "sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml cp /tmp/kordinate-pass.tar.gz master/$POD:/tmp/kordinate-pass.tar.gz -c workstation"
          ws_exec "$NODE" "cd /home/claude && tar xzf /tmp/kordinate-pass.tar.gz && rm /tmp/kordinate-pass.tar.gz"
          rm -f "$TMP_PASS"
          log "Pass store copied to workstation"
          ;;
      esac
    fi
  else
    info "No GPG key provided — will create fresh on workstation"
  fi

  # ─── Step 6: Run auth check on workstation ───
  echo ""
  echo -e "${BOLD}Step 6: Auth setup${NC}"

  # Copy the auth-check script and run it
  local AUTH_SCRIPT="$SCRIPT_DIR/setup/auth-check.sh"
  if [ -f "$AUTH_SCRIPT" ]; then
    local POD
    POD=$(ssh "$NODE" "sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml get pod -n master -l component=workstation -o jsonpath='{.items[0].metadata.name}'")
    scp "$AUTH_SCRIPT" "$NODE:/tmp/kordinate-auth-check.sh"
    ssh "$NODE" "sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml cp /tmp/kordinate-auth-check.sh master/$POD:/tmp/auth-check.sh -c workstation"
    # Run interactively via kubectl exec with TTY
    ssh -t "$NODE" "sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml exec -it -n master deploy/workstation -c workstation -- bash /tmp/auth-check.sh"
  fi

  echo ""
  log "Setup complete!"
  echo ""
  echo "  SSH in with: ssh workstation"
  echo "  Then run:    claude login"
}

# ═══════════════════════════════════════════════════════════════
# HYDRATE — generate .mcp.json from config.yaml + pass
# (runs on the workstation, not the initial machine)
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

  _read_config() {
    python3 -c "
import yaml, sys
c = yaml.safe_load(open('$CONFIG'))
path = sys.argv[1].split('.')
v = c
for p in path:
    if isinstance(v, dict) and p in v:
        v = v[p]
    else:
        sys.exit(0)
print(v)
" "$1" 2>/dev/null || true
  }

  local DC_IP HOME_IP
  DC_IP=$(_read_config clusters.datacenter.tailscale_ip)
  HOME_IP=$(_read_config clusters.home.tailscale_ip)

  local DC_PG_PORT DC_PG_USER DC_PG_DB HOME_PG_PORT HOME_PG_USER HOME_PG_DB
  DC_PG_PORT=$(_read_config clusters.datacenter.services.postgres.port)
  DC_PG_USER=$(_read_config clusters.datacenter.services.postgres.user)
  DC_PG_DB=$(_read_config clusters.datacenter.services.postgres.database)
  HOME_PG_PORT=$(_read_config clusters.home.services.postgres.port)
  HOME_PG_USER=$(_read_config clusters.home.services.postgres.user)
  HOME_PG_DB=$(_read_config clusters.home.services.postgres.database)

  local GRAFANA_PORT GRAFANA_TOKEN
  GRAFANA_PORT=$(_read_config clusters.home.services.grafana.port)
  GRAFANA_TOKEN=$(pass show kordinate/grafana_admin/api_key 2>/dev/null || echo "")

  local DC_REDIS_PORT
  DC_REDIS_PORT=$(_read_config clusters.datacenter.services.redis.port)

  echo "Generating .mcp.json..."

  python3 -c "
import json

mcp = {'mcpServers': {}}

dc_ip = '''$DC_IP'''
home_ip = '''$HOME_IP'''

# Postgres datacenter
if dc_ip and '''$DC_PG_PORT''':
    mcp['mcpServers']['postgres-datacenter'] = {
        'command': 'npx',
        'args': ['-y', '@modelcontextprotocol/server-postgres',
                 f'postgresql://$DC_PG_USER@{dc_ip}:$DC_PG_PORT/$DC_PG_DB']
    }

# Postgres home
if home_ip and '''$HOME_PG_PORT''':
    mcp['mcpServers']['postgres-home'] = {
        'command': 'npx',
        'args': ['-y', '@modelcontextprotocol/server-postgres',
                 f'postgresql://$HOME_PG_USER@{home_ip}:$HOME_PG_PORT/$HOME_PG_DB']
    }

# Grafana
if home_ip and '''$GRAFANA_PORT''':
    env = {
        'GRAFANA_URL': f'http://{home_ip}:$GRAFANA_PORT'
    }
    token = '''$GRAFANA_TOKEN'''
    if token:
        env['GRAFANA_SERVICE_ACCOUNT_TOKEN'] = token
    mcp['mcpServers']['grafana-admin'] = {
        'command': 'uvx',
        'args': ['mcp-grafana'],
        'env': env
    }

# Redis datacenter
if dc_ip and '''$DC_REDIS_PORT''':
    mcp['mcpServers']['redis-datacenter'] = {
        'command': 'npx',
        'args': ['-y', '@modelcontextprotocol/server-redis'],
        'env': {
            'REDIS_HOST': dc_ip,
            'REDIS_PORT': '$DC_REDIS_PORT'
        }
    }

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
# BOOTSTRAP — cluster infrastructure (separate from workstation)
# ═══════════════════════════════════════════════════════════════

SETUP_CLUSTER="$SCRIPT_DIR/agents/deployer/manifests/bootstrap/setup-cluster.sh"
CLUSTER_BOOTSTRAP="$SCRIPT_DIR/bin/cluster-bootstrap"
RBAC_MANIFEST="$SCRIPT_DIR/agents/deployer/manifests/rbac/agent-rbac.yaml"
GATEWAY_MANIFESTS="$SCRIPT_DIR/agents/deployer/manifests/gateway"

prompt_node() {
  local var_name="$1"
  local prompt_msg="$2"
  local default="${3:-}"
  if [ -n "$default" ]; then
    read -rp "$prompt_msg [$default]: " value
    eval "$var_name=\"${value:-$default}\""
  else
    read -rp "$prompt_msg: " value
    if [ -z "$value" ]; then
      err "No value provided"
      exit 1
    fi
    eval "$var_name=\"$value\""
  fi
}

cmd_bootstrap() {
  local SUBCMD="${1:-}"

  case "$SUBCMD" in
    cluster)
      prompt_node NODE "SSH address of cluster node"
      local subcmd="${2:-server}"
      ssh "$NODE" "bash -s $subcmd" < "$SETUP_CLUSTER"
      ;;
    rbac)
      prompt_node NODE "SSH address of cluster node"
      scp "$RBAC_MANIFEST" "$NODE:/tmp/agent-rbac.yaml"
      ssh "$NODE" "bash -s" < "$CLUSTER_BOOTSTRAP"
      log "RBAC bootstrap complete"
      ;;
    gateway)
      prompt_node NODE "SSH address of cluster node"
      local overlays=()
      for d in "$GATEWAY_MANIFESTS"/overlays/*/; do
        [ -d "$d" ] || continue
        overlays+=("$(basename "$d")")
      done
      local i=1
      for o in "${overlays[@]}"; do echo "  $i) $o"; ((i++)); done
      read -rp "Overlay [1]: " choice
      local overlay="${overlays[${choice:-1}-1]:-${overlays[0]}}"
      read -rp "Tailscale auth key: " TS_AUTH_KEY
      [ -z "$TS_AUTH_KEY" ] && { err "Required"; exit 1; }

      remote_kc "$NODE" "create namespace gateway --dry-run=client -o yaml | sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml apply -f -"
      remote_kc "$NODE" "create secret generic tailscale-auth -n gateway --from-literal=AUTH_KEY=$TS_AUTH_KEY --dry-run=client -o yaml | sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml apply -f -"
      local tmp_dir="/tmp/kordinate-gateway"
      ssh "$NODE" "rm -rf $tmp_dir && mkdir -p $tmp_dir"
      scp -r "$GATEWAY_MANIFESTS/base" "$NODE:$tmp_dir/base"
      scp -r "$GATEWAY_MANIFESTS/overlays/$overlay" "$NODE:$tmp_dir/overlay"
      ssh "$NODE" "cd $tmp_dir/overlay && sed -i 's|../../base|../base|' kustomization.yaml"
      remote_kc "$NODE" "apply -k $tmp_dir/overlay"
      log "Gateway deployed ($overlay)"
      ;;
    master)
      prompt_node NODE "SSH address of cluster node"
      local tmp_dir="/tmp/kordinate-master"
      ssh "$NODE" "rm -rf $tmp_dir && mkdir -p $tmp_dir"
      scp -r "$MASTER_MANIFESTS/base" "$NODE:$tmp_dir/base"
      remote_kc "$NODE" "create namespace master --dry-run=client -o yaml | sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml apply -f -"
      remote_kc "$NODE" "apply -k $tmp_dir/base"
      log "Master manifests applied"
      ;;
    *)
      echo "Usage: ./setup.sh bootstrap <cluster|rbac|gateway|master>"
      ;;
  esac
}

# ═══════════════════════════════════════════════════════════════
# MAIN DISPATCHER
# ═══════════════════════════════════════════════════════════════
usage() {
  echo "Usage: ./setup.sh [command]"
  echo ""
  echo "  (no args)     Deploy workstation and set up auth"
  echo "  bootstrap      Cluster infrastructure (k3s, RBAC, gateway)"
  echo "  hydrate        Generate .mcp.json from config.yaml + pass"
  echo "  export         Bundle GPG key + pass store → encrypted archive"
  echo "  import         Restore GPG key + pass store from archive"
}

case "${CMD:-setup}" in
  setup|"")  cmd_setup ;;
  hydrate)   cmd_hydrate ;;
  bootstrap) cmd_bootstrap "${@:2}" ;;
  export)    cmd_export "${@:2}" ;;
  import)    cmd_import "${@:2}" ;;
  *) usage; exit 1 ;;
esac
