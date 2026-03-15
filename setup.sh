#!/bin/bash
# Setup kordinate environment.
#
# Usage:
#   ./setup.sh install      # Copy framework → ~/.claude/
#   ./setup.sh profile      # Scaffold config + initialize pass store
#   ./setup.sh hydrate      # Generate .mcp.json from config.yaml + pass
#   ./setup.sh shell        # PATH, CLAUDE_HOME, tmux, claude alias → shell RC
#   ./setup.sh doctor       # Check prerequisites, framework, profile, connectivity
#   ./setup.sh bootstrap    # Orchestrate cluster setup from scratch
#   ./setup.sh export       # Bundle profile + keys → encrypted archive
#   ./setup.sh import       # Restore from encrypted archive
#   ./setup.sh uninstall    # Remove everything kordinate installed
#   ./setup.sh client       # SSH config for remote workstation access
#   ./setup.sh [no args]    # Interactive: install → import or scaffold → shell

set -euo pipefail

CLAUDE_HOME="$HOME/.claude"
export CLAUDE_HOME
source "$CLAUDE_HOME/setup/lib.sh"

CMD="${1:-}"

# ═══════════════════════════════════════════════════════════════
# PROFILE — scaffold config + init pass store
# ═══════════════════════════════════════════════════════════════
cmd_profile() {
  cd "$CLAUDE_DIR"

  _create() {
    local file="$1"
    if [ -f "$file" ]; then
      echo "  SKIP $file (already exists)"
      return 1
    fi
    mkdir -p "$(dirname "$file")"
    echo "  CREATE $file"
    return 0
  }

  echo "Scaffolding profile at ~/.claude/..."

  # ─── profile/config.yaml ───
  if _create profile/config.yaml; then
cat > profile/config.yaml << 'CONFIG'
# Centralized Configuration
# All cluster IPs, ports, hostnames, and service endpoints in one place.
# Referenced by deploy configs, MCP servers, monitoring, and bin/ scripts.
#
# Non-secret metadata (tailnet name, account IDs, etc.) also lives here.

tailscale:
  api_base: https://api.tailscale.com/api/v2
  tailnet: tailXXXXXX.ts.net

grafana:
  admin_user: admin

cloudflare:
  account_id: your-account-id
  tunnel_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  tunnel_name: grafana-master

clusters:
  datacenter:
    name: datacenter
    description: Datacenter cluster (multi-node k3s)
    tailscale_ip: 100.x.x.x
    lan_network: 10.0.0.0/24
    gateway_lan_ip: 10.0.0.1
    nodes:
      - 10.0.0.1  # ctrl (gateway)
      - 10.0.0.2
      - 10.0.0.3
    namespaces: [dev, test, prod]
    manifests:
      gateway: agents/deployer/manifests/gateway
      bootstrap: agents/deployer/manifests/bootstrap
      platform: profile/additions
    services:
      postgres:
        port: 30632
        user: myuser
        database: postgres
      redis:
        port: 30379
      metrics:
        port: 30091
      logs:
        port: 30101
      registry:
        port: 5000
        host: 10.0.0.1
        url: 10.0.0.1:5000

  home:
    name: home
    description: Home cluster (k3s)
    tailscale_ip: 100.x.x.x
    nodes:
      - 192.168.x.x
    namespaces: [dev, test, prod]
    manifests:
      gateway: agents/deployer/manifests/gateway
      master: agents/deployer/manifests/master
      bootstrap: agents/deployer/manifests/bootstrap
      platform: profile/additions
    services:
      postgres:
        port: 30633
        user: myuser
        database: mydb
      redis:
        port: 30380
      metrics:
        port: 30091
      logs:
        port: 30101
      grafana:
        port: 30300
        namespace: master

network:
  tailnet: tailXXXXXX.ts.net
  grafana_public: grafana.example.com

node_hostnames:
  node-1: 10.0.0.1
  node-2: 10.0.0.2
  node-3: 10.0.0.3
CONFIG
  fi

  # ─── Root config.yaml ───
  if _create config.yaml; then
    cp profile/config.yaml config.yaml
  fi

  # ─── profile/additions directory ───
  mkdir -p profile/additions
  echo "  ENSURE profile/additions/ directory"

  # ─── profile/conventions.md ───
  if _create profile/conventions.md; then
cat > profile/conventions.md << 'CONV'
# Conventions

Project-specific conventions and standards. Referenced by agents for
consistency. Add your team's conventions here.
CONV
  fi

  # ─── Deploy config example ───
  if _create agents/deployer/deploys/example.yaml; then
cat > agents/deployer/deploys/example.yaml << 'DEPLOY'
# Deploy configuration — one file per project, tracked by the deployer agent.
# Copy this to <project>.yaml and fill in your values.

project: myproject
repo: https://github.com/org/myproject
cluster: datacenter
method: kubectl        # kubectl or git-branch
image: 10.0.0.1:5000/myproject:latest

branches:
  dev: main
  test: test
  prod: prod

dev:
  status: running
  namespace: dev
  components: [api, worker]

test:
  status: scaled-down
  namespace: test
  components: [api, worker]

prod:
  status: running
  namespace: prod
  components: [api, worker]
DEPLOY
  fi

  # ─── Initialize pass store ───
  echo ""
  echo "Setting up pass store for credentials..."

  local GPG_KEY_ID
  GPG_KEY_ID=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep -m1 '^sec' | awk '{print $2}' | cut -d/ -f2 || true)

  if [ -z "$GPG_KEY_ID" ]; then
    warn "No GPG secret key found — cannot initialize pass store"
    echo "  Create one with: gpg --full-generate-key"
    echo "  Then re-run: ./setup.sh profile"
    echo ""
    echo "Done (partial). Config scaffolded, but pass store needs GPG key."
    return 0
  fi

  if [ ! -d "$HOME/.password-store" ]; then
    pass init "$GPG_KEY_ID"
    log "Initialized pass store with GPG key $GPG_KEY_ID"
  fi

  local PASS_KEYS=(
    tailscale/api_key
    tailscale/auth_key_gateway
    tailscale/auth_key_workstation
    grafana_admin/api_key
    grafana_home/api_key
    grafana_vandc/api_key
    gemini/api_key
    cloudflare/api_token
    cloudflare/tunnel_token
  )

  local key
  for key in "${PASS_KEYS[@]}"; do
    if ! pass show "kordinate/$key" &>/dev/null; then
      echo "PLACEHOLDER" | pass insert -e "kordinate/$key" 2>/dev/null
      echo "  CREATE pass:kordinate/$key (placeholder)"
    else
      echo "  SKIP pass:kordinate/$key (already exists)"
    fi
  done

  echo ""
  cmd_hydrate

  echo ""
  echo "Done. Fill in config.yaml IPs, then set real keys with:"
  echo "  pass edit kordinate/<service>/<key>"
  echo "  ./setup.sh hydrate   # regenerate .mcp.json after changes"
}

# ═══════════════════════════════════════════════════════════════
# HYDRATE — generate .mcp.json from config.yaml + pass
# ═══════════════════════════════════════════════════════════════
cmd_hydrate() {
  local CONFIG="$CLAUDE_DIR/config.yaml"

  if [ ! -f "$CONFIG" ]; then
    err "config.yaml not found at $CONFIG"
    echo "  Run: ./setup.sh profile"
    exit 1
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
" > "$CLAUDE_DIR/.mcp.json"

  log "Generated .mcp.json at $CLAUDE_DIR/.mcp.json"

  if [ -f "$CLAUDE_DIR/profile/config.yaml" ] && [ ! -f "$CLAUDE_DIR/config.yaml" ]; then
    cp "$CLAUDE_DIR/profile/config.yaml" "$CLAUDE_DIR/config.yaml"
    log "Copied profile/config.yaml → config.yaml"
  fi
}

# ═══════════════════════════════════════════════════════════════
# SHELL — PATH, CLAUDE_HOME, tmux, claude alias → shell RC
# ═══════════════════════════════════════════════════════════════
cmd_shell() {
  echo "Configuring shell profile: $SHELL_RC"

  # Symlink tmux config
  if [ -f "$CLAUDE_HOME/bin/tmux.conf" ]; then
    cp "$CLAUDE_HOME/bin/tmux.conf" "$HOME/.tmux.conf"
    echo "  COPY ~/.tmux.conf"
  fi

  # tmux-session.bash
  if [ -f "$CLAUDE_HOME/bin/tmux-session.bash" ]; then
    local SOURCE_LINE="source \"$CLAUDE_HOME/bin/tmux-session.bash\""
    if ! grep -qF "tmux-session.bash" "$SHELL_RC" 2>/dev/null; then
      echo "" >> "$SHELL_RC"
      echo "# koordinate tmux session management" >> "$SHELL_RC"
      echo "$SOURCE_LINE" >> "$SHELL_RC"
      echo "  ADD  $SHELL_RC: source tmux-session.bash"
    else
      echo "  SKIP tmux-session.bash (already in $SHELL_RC)"
    fi
  fi

  # CLAUDE_HOME
  if ! grep -q "export CLAUDE_HOME=" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# koordinate home" >> "$SHELL_RC"
    echo "export CLAUDE_HOME=\"$CLAUDE_HOME\"" >> "$SHELL_RC"
    echo "  ADD  $SHELL_RC: CLAUDE_HOME"
  else
    echo "  SKIP CLAUDE_HOME (already in $SHELL_RC)"
  fi

  # bin to PATH
  local REPO_BASENAME
  REPO_BASENAME="$(basename "$CLAUDE_HOME")"
  if ! grep -q "export PATH=.*$REPO_BASENAME/bin" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# $REPO_BASENAME tools" >> "$SHELL_RC"
    echo "export PATH=\"$CLAUDE_HOME/bin:\$PATH\"" >> "$SHELL_RC"
    echo "  ADD  $SHELL_RC: $REPO_BASENAME/bin to PATH"
  else
    echo "  SKIP $REPO_BASENAME/bin (already in PATH)"
  fi

  # claude → claude-session alias
  if ! grep -qF "claude-session" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Claude Code: auto-worktree sessions" >> "$SHELL_RC"
    echo "alias claude=\"claude-session --dangerously-skip-permissions\"" >> "$SHELL_RC"
    echo "  ADD  $SHELL_RC: claude → claude-session alias"
  else
    echo "  SKIP claude alias (already in $SHELL_RC)"
  fi

  # Default working directory
  if ! grep -q "cd.*$REPO_BASENAME" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Default working directory" >> "$SHELL_RC"
    echo "cd $CLAUDE_HOME 2>/dev/null" >> "$SHELL_RC"
    echo "  ADD  $SHELL_RC: default cd → $CLAUDE_HOME"
  else
    echo "  SKIP default cd (already in $SHELL_RC)"
  fi

  echo ""
  echo "Shell configuration complete. Run: source $SHELL_RC"
}

# ═══════════════════════════════════════════════════════════════
# CLIENT — SSH config for remote workstation access
# ═══════════════════════════════════════════════════════════════
cmd_client() {
  local SSH_CONFIG="$HOME/.ssh/config"
  local MARKER="# kordinate master access"
  if ! grep -q "$MARKER" "$SSH_CONFIG" 2>/dev/null; then
    mkdir -p "$HOME/.ssh"
    cat >> "$SSH_CONFIG" <<SSH_EOF

# kordinate master access
Host master
  HostName workstation
  Port 2222
  User claude
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
SSH_EOF
    chmod 600 "$SSH_CONFIG"
    echo "  ADD  SSH config: master → workstation (Tailscale)"
  else
    echo "  SKIP SSH config (already configured)"
  fi
}

# ═══════════════════════════════════════════════════════════════
# EXPORT — bundle profile + keys → encrypted archive
# ═══════════════════════════════════════════════════════════════
cmd_export() {
  local OUTPUT="${1:-kordinate-export.gpg}"
  local WORK_DIR
  WORK_DIR="$(mktemp -d)"
  trap 'rm -rf "$WORK_DIR"' EXIT

  echo "Collecting profile files..."
  cd "$CLAUDE_DIR"

  local PROFILE_DIR="$WORK_DIR/profile"
  mkdir -p "$PROFILE_DIR"

  local f
  for f in profile/config.yaml profile/conventions.md config.yaml; do
    if [ -f "$f" ]; then
      mkdir -p "$PROFILE_DIR/$(dirname "$f")"
      cp "$f" "$PROFILE_DIR/$f"
      echo "  + $f"
    fi
  done

  if [ -d "profile/additions" ] && [ "$(ls -A profile/additions 2>/dev/null)" ]; then
    mkdir -p "$PROFILE_DIR/profile/additions"
    cp -r profile/additions/* "$PROFILE_DIR/profile/additions/"
    echo "  + profile/additions/"
  fi

  if [ -d "agents/deployer/deploys" ]; then
    mkdir -p "$PROFILE_DIR/agents/deployer/deploys"
    for f in agents/deployer/deploys/*.yaml; do
      [ -f "$f" ] || continue
      cp "$f" "$PROFILE_DIR/$f"
      echo "  + $f"
    done
  fi

  local agent_dir
  for agent_dir in agents/*/; do
    [ -d "$agent_dir" ] || continue
    for f in memory.md inbox.md; do
      if [ -f "$agent_dir/$f" ]; then
        mkdir -p "$PROFILE_DIR/$agent_dir"
        cp "$agent_dir/$f" "$PROFILE_DIR/$agent_dir/$f"
        echo "  + $agent_dir$f"
      fi
    done
  done

  if [ -d "agent-state" ]; then
    mkdir -p "$PROFILE_DIR/agent-state"
    cp -r agent-state/* "$PROFILE_DIR/agent-state/" 2>/dev/null || true
    echo "  + agent-state/"
  fi

  # Decrypt pass entries
  echo ""
  echo "Collecting keys from pass store..."

  local KEYS_DIR="$WORK_DIR/keys"
  mkdir -p "$KEYS_DIR"

  local KEY_COUNT=0 entry key_path value
  while IFS= read -r entry; do
    key_path="${entry#kordinate/}"
    [ -z "$key_path" ] && continue
    value=$(pass show "$entry" 2>/dev/null) || continue
    mkdir -p "$KEYS_DIR/$(dirname "$key_path")"
    echo "$value" > "$KEYS_DIR/$key_path"
    echo "  + $key_path"
    ((KEY_COUNT++)) || true
  done < <(pass ls kordinate/ 2>/dev/null | grep -oP '── \K.*' | sed 's/^/kordinate\//' || true)

  # Fallback: walk .gpg files directly
  if [ "$KEY_COUNT" -eq 0 ] && [ -d "$HOME/.password-store/kordinate" ]; then
    local gpg_file rel
    while IFS= read -r gpg_file; do
      rel="${gpg_file#$HOME/.password-store/}"
      rel="${rel%.gpg}"
      key_path="${rel#kordinate/}"
      value=$(pass show "$rel" 2>/dev/null) || continue
      mkdir -p "$KEYS_DIR/$(dirname "$key_path")"
      echo "$value" > "$KEYS_DIR/$key_path"
      echo "  + $key_path"
      ((KEY_COUNT++)) || true
    done < <(find "$HOME/.password-store/kordinate" -name '*.gpg' -type f 2>/dev/null)
  fi

  echo "  $KEY_COUNT key(s) collected"

  echo ""
  echo "Creating encrypted archive..."
  local TMPTAR="$WORK_DIR/bundle.tar.gz"
  tar czf "$TMPTAR" -C "$WORK_DIR" profile keys
  gpg --batch --yes --symmetric --cipher-algo AES256 -o "$OUTPUT" "$TMPTAR"

  echo ""
  log "Export complete: $OUTPUT"
  echo "  Store this file securely. Use './setup.sh import $OUTPUT' to restore."
}

# ═══════════════════════════════════════════════════════════════
# IMPORT — restore from encrypted archive
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

  if [ ! -d "$WORK_DIR/profile" ]; then
    err "Invalid archive — no profile directory found"
    exit 1
  fi

  echo ""
  echo "Restoring profile files..."
  mkdir -p "$CLAUDE_DIR"

  local f
  cd "$WORK_DIR/profile"
  find . -type f | while IFS= read -r f; do
    f="${f#./}"
    mkdir -p "$CLAUDE_DIR/$(dirname "$f")"
    cp "$f" "$CLAUDE_DIR/$f"
    echo "  + $f"
  done

  echo ""
  echo "Restoring keys to pass store..."

  local GPG_KEY_ID
  GPG_KEY_ID=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep -m1 '^sec' | awk '{print $2}' | cut -d/ -f2 || true)

  if [ -z "$GPG_KEY_ID" ]; then
    echo ""
    warn "No GPG secret key found. You need one for the pass store."
    echo "  Create one with: gpg --full-generate-key"
    echo "  Then re-run: ./setup.sh import $ARCHIVE"
    exit 1
  fi

  if [ ! -d "$HOME/.password-store" ]; then
    pass init "$GPG_KEY_ID"
    log "Initialized pass store with GPG key $GPG_KEY_ID"
  fi

  if [ -d "$WORK_DIR/keys" ]; then
    local KEY_COUNT value
    cd "$WORK_DIR/keys"
    find . -type f | while IFS= read -r f; do
      f="${f#./}"
      value=$(cat "$f")
      echo "$value" | pass insert -e "kordinate/$f" 2>/dev/null
      echo "  + kordinate/$f"
    done
    KEY_COUNT=$(find . -type f | wc -l)
    log "$KEY_COUNT key(s) imported to pass store"
  else
    warn "No keys found in archive"
  fi

  echo ""
  cmd_hydrate

  echo ""
  log "Import complete. Run './setup.sh doctor' to verify."
}

# ═══════════════════════════════════════════════════════════════
# BOOTSTRAP — orchestrate cluster setup from scratch
# ═══════════════════════════════════════════════════════════════

SETUP_CLUSTER="$CLAUDE_HOME/agents/deployer/manifests/bootstrap/setup-cluster.sh"
CLUSTER_BOOTSTRAP="$CLAUDE_HOME/bin/cluster-bootstrap"
RBAC_MANIFEST="$CLAUDE_HOME/agents/deployer/manifests/rbac/agent-rbac.yaml"
GATEWAY_MANIFESTS="$CLAUDE_HOME/agents/deployer/manifests/gateway"
MASTER_MANIFESTS="$CLAUDE_HOME/agents/deployer/manifests/master"

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

ssh_node() {
  local node="$1"; shift
  ssh -o ConnectTimeout=10 -o BatchMode=yes "$node" "$@"
}

get_cluster_ip() {
  local cluster="$1"
  python3 -c "import yaml; c=yaml.safe_load(open('$CLAUDE_DIR/config.yaml')); print(c['clusters']['$cluster']['tailscale_ip'])" 2>/dev/null || true
}

remote_kc() {
  local node="$1"; shift
  ssh "$node" "sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml $*"
}

bootstrap_status() {
  echo -e "${BOLD}Bootstrap Status${NC}"
  echo ""

  if [ ! -f "$CLAUDE_DIR/config.yaml" ] || grep -q '100\.x\.x\.x' "$CLAUDE_DIR/config.yaml" 2>/dev/null; then
    warn "config.yaml not configured — cannot check cluster status"
    echo "  Run: ./setup.sh profile (then fill in real IPs)"
    return
  fi

  local cluster ip
  for cluster in $(python3 -c "import yaml; c=yaml.safe_load(open('$CLAUDE_DIR/config.yaml')); print(' '.join(c.get('clusters',{}).keys()))" 2>/dev/null); do
    echo -e "\n${BOLD}Cluster: $cluster${NC}"
    ip=$(get_cluster_ip "$cluster")

    if [ -z "$ip" ]; then
      warn "no Tailscale IP configured"
      continue
    fi

    if ! ssh -o ConnectTimeout=3 -o BatchMode=yes "$ip" true &>/dev/null; then
      err "  unreachable at $ip"
      continue
    fi
    log "reachable at $ip"

    if ssh_node "$ip" "systemctl is-active k3s" &>/dev/null; then
      log "k3s running"
    elif ssh_node "$ip" "systemctl is-active k3s-agent" &>/dev/null; then
      log "k3s-agent running"
    else
      err "  k3s not running"
      continue
    fi

    local nodes ns_list
    nodes=$(remote_kc "$ip" "get nodes --no-headers 2>/dev/null" | wc -l)
    log "$nodes node(s)"

    ns_list=$(remote_kc "$ip" "get ns --no-headers 2>/dev/null" | awk '{print $1}' | tr '\n' ' ')
    info "namespaces: $ns_list"

    if echo "$ns_list" | grep -q gateway; then
      log "gateway namespace exists"
      local gw_pods
      gw_pods=$(remote_kc "$ip" "get pods -n gateway --no-headers 2>/dev/null" | wc -l)
      info "  gateway pods: $gw_pods"
    else
      warn "gateway namespace missing"
    fi

    if echo "$ns_list" | grep -q master; then
      log "master namespace exists"
      local master_pods
      master_pods=$(remote_kc "$ip" "get pods -n master --no-headers 2>/dev/null" | wc -l)
      info "  master pods: $master_pods"
    fi

    if remote_kc "$ip" "get serviceaccount agent-readonly -n kube-system" &>/dev/null; then
      log "RBAC configured (agent-readonly SA)"
    else
      warn "RBAC not configured"
    fi
  done
}

bootstrap_cluster() {
  echo -e "${BOLD}Cluster Setup${NC}"
  echo ""

  prompt_node NODE "SSH address of control plane node (user@ip or Tailscale IP)"

  local subcmd="${1:-}"
  if [ -z "$subcmd" ]; then
    echo ""
    echo "What to install?"
    echo "  1) server       — k3s control plane"
    echo "  2) agent        — k3s worker node"
    echo "  3) post-install — namespaces, Longhorn, storage"
    read -rp "Choice [1]: " choice
    case "${choice:-1}" in
      1) subcmd="server" ;;
      2) subcmd="agent" ;;
      3) subcmd="post-install" ;;
      *) err "Invalid choice"; exit 1 ;;
    esac
  fi

  info "Running setup-cluster.sh $subcmd on $NODE..."
  ssh "$NODE" "bash -s $subcmd" < "$SETUP_CLUSTER"
}

bootstrap_rbac() {
  echo -e "${BOLD}RBAC Bootstrap${NC}"
  echo ""

  prompt_node NODE "SSH address of cluster node"

  info "Copying agent-rbac.yaml to $NODE..."
  scp "$RBAC_MANIFEST" "$NODE:/tmp/agent-rbac.yaml"

  info "Running cluster-bootstrap on $NODE..."
  ssh "$NODE" "bash -s" < "$CLUSTER_BOOTSTRAP"

  log "RBAC bootstrap complete"
}

bootstrap_gateway() {
  echo -e "${BOLD}Gateway Setup${NC}"
  echo ""

  prompt_node NODE "SSH address of cluster node"

  echo ""
  echo "Which cluster overlay?"
  local overlays=()
  local d
  for d in "$GATEWAY_MANIFESTS"/overlays/*/; do
    [ -d "$d" ] || continue
    overlays+=("$(basename "$d")")
  done

  if [ ${#overlays[@]} -eq 0 ]; then
    err "No gateway overlays found at $GATEWAY_MANIFESTS/overlays/"
    exit 1
  fi

  local i=1 o
  for o in "${overlays[@]}"; do
    echo "  $i) $o"
    ((i++))
  done
  read -rp "Choice [1]: " choice
  local overlay="${overlays[${choice:-1}-1]:-${overlays[0]}}"

  echo ""
  read -rp "Tailscale auth key (tskey-auth-...): " TS_AUTH_KEY
  if [ -z "$TS_AUTH_KEY" ]; then
    err "Tailscale auth key required for gateway"
    exit 1
  fi

  info "Creating Tailscale auth secret on $NODE..."
  remote_kc "$NODE" "create namespace gateway --dry-run=client -o yaml | sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml apply -f -"
  remote_kc "$NODE" "create secret generic tailscale-auth -n gateway --from-literal=AUTH_KEY=$TS_AUTH_KEY --dry-run=client -o yaml | sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml apply -f -"

  info "Applying gateway overlay: $overlay..."
  local tmp_dir="/tmp/kordinate-gateway"
  ssh "$NODE" "rm -rf $tmp_dir && mkdir -p $tmp_dir"
  scp -r "$GATEWAY_MANIFESTS/base" "$NODE:$tmp_dir/base"
  scp -r "$GATEWAY_MANIFESTS/overlays/$overlay" "$NODE:$tmp_dir/overlay"
  ssh "$NODE" "cd $tmp_dir/overlay && sed -i 's|../../base|../base|' kustomization.yaml"
  remote_kc "$NODE" "apply -k $tmp_dir/overlay"

  log "Gateway deployed ($overlay overlay)"
}

bootstrap_master() {
  echo -e "${BOLD}Master Setup${NC}"
  echo ""

  prompt_node NODE "SSH address of master cluster node"

  info "Applying master manifests..."
  local tmp_dir="/tmp/kordinate-master"
  ssh "$NODE" "rm -rf $tmp_dir && mkdir -p $tmp_dir"
  scp -r "$MASTER_MANIFESTS/base" "$NODE:$tmp_dir/base"

  remote_kc "$NODE" "create namespace master --dry-run=client -o yaml | sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml apply -f -"
  remote_kc "$NODE" "apply -k $tmp_dir/base"

  log "Master manifests applied"
}

bootstrap_platform() {
  echo -e "${BOLD}Platform Setup${NC}"
  echo ""

  local additions="$CLAUDE_DIR/profile/additions"
  if [ ! -d "$additions" ] || [ -z "$(ls -A "$additions" 2>/dev/null)" ]; then
    warn "No platform additions at $additions"
    echo "  Add manifests to ~/.claude/profile/additions/ and retry"
    return
  fi

  prompt_node NODE "SSH address of cluster node"

  info "Syncing platform additions to $NODE..."
  local tmp_dir="/tmp/kordinate-platform"
  ssh "$NODE" "rm -rf $tmp_dir && mkdir -p $tmp_dir"
  scp -r "$additions/"* "$NODE:$tmp_dir/"

  if ssh "$NODE" "test -f $tmp_dir/kustomization.yaml"; then
    remote_kc "$NODE" "apply -k $tmp_dir"
  else
    remote_kc "$NODE" "apply -R -f $tmp_dir"
  fi

  log "Platform additions applied"
}

bootstrap_full() {
  echo -e "${BOLD}Full Bootstrap${NC}"
  echo "This will guide you through setting up a cluster from scratch."
  echo ""

  info "Step 1/8: Checking prerequisites..."
  if ! "$CLAUDE_HOME/setup/doctor.sh" --category prereqs; then
    err "Prerequisites not met — fix the above and retry"
    exit 1
  fi

  echo ""
  info "Step 2/8: Cluster target"
  prompt_node NODE "SSH address of control plane node (user@ip)"

  echo ""
  info "Step 3/8: Installing k3s server..."
  read -rp "Install k3s server on $NODE? [Y/n] " answer
  case "${answer:-y}" in
    [nN]*) info "Skipping k3s install" ;;
    *)
      ssh "$NODE" "bash -s server" < "$SETUP_CLUSTER"
      log "k3s server installed"
      ;;
  esac

  echo ""
  info "Step 4/8: Post-install (namespaces, Longhorn)..."
  read -rp "Run post-install on $NODE? [Y/n] " answer
  case "${answer:-y}" in
    [nN]*) info "Skipping post-install" ;;
    *)
      ssh "$NODE" "bash -s post-install" < "$SETUP_CLUSTER"
      log "Post-install complete"
      ;;
  esac

  echo ""
  info "Step 5/8: Agent RBAC..."
  read -rp "Bootstrap RBAC on $NODE? [Y/n] " answer
  case "${answer:-y}" in
    [nN]*) info "Skipping RBAC" ;;
    *)
      scp "$RBAC_MANIFEST" "$NODE:/tmp/agent-rbac.yaml"
      ssh "$NODE" "bash -s" < "$CLUSTER_BOOTSTRAP"
      log "RBAC bootstrap complete"
      ;;
  esac

  echo ""
  info "Step 6/8: Gateway (Tailscale + monitoring)..."
  read -rp "Deploy gateway on $NODE? [Y/n] " answer
  case "${answer:-y}" in
    [nN]*) info "Skipping gateway" ;;
    *)
      local overlays=()
      local d
      for d in "$GATEWAY_MANIFESTS"/overlays/*/; do
        [ -d "$d" ] || continue
        overlays+=("$(basename "$d")")
      done
      local i=1 o
      for o in "${overlays[@]}"; do
        echo "  $i) $o"
        ((i++))
      done
      read -rp "Overlay [1]: " choice
      local overlay="${overlays[${choice:-1}-1]:-${overlays[0]}}"

      read -rp "Tailscale auth key: " TS_AUTH_KEY
      if [ -z "$TS_AUTH_KEY" ]; then
        err "Tailscale auth key required"; exit 1
      fi

      remote_kc "$NODE" "create namespace gateway --dry-run=client -o yaml | sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml apply -f -"
      remote_kc "$NODE" "create secret generic tailscale-auth -n gateway --from-literal=AUTH_KEY=$TS_AUTH_KEY --dry-run=client -o yaml | sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml apply -f -"

      local tmp_dir="/tmp/kordinate-gateway"
      ssh "$NODE" "rm -rf $tmp_dir && mkdir -p $tmp_dir"
      scp -r "$GATEWAY_MANIFESTS/base" "$NODE:$tmp_dir/base"
      scp -r "$GATEWAY_MANIFESTS/overlays/$overlay" "$NODE:$tmp_dir/overlay"
      ssh "$NODE" "cd $tmp_dir/overlay && sed -i 's|../../base|../base|' kustomization.yaml"
      remote_kc "$NODE" "apply -k $tmp_dir/overlay"
      log "Gateway deployed"
      ;;
  esac

  echo ""
  info "Step 7/8: Master (Grafana, workstation)..."
  read -rp "Is this the master cluster? [y/N] " answer
  case "${answer:-n}" in
    [yY]*)
      local tmp_dir="/tmp/kordinate-master"
      ssh "$NODE" "rm -rf $tmp_dir && mkdir -p $tmp_dir"
      scp -r "$MASTER_MANIFESTS/base" "$NODE:$tmp_dir/base"
      remote_kc "$NODE" "create namespace master --dry-run=client -o yaml | sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml apply -f -"
      remote_kc "$NODE" "apply -k $tmp_dir/base"
      log "Master manifests applied"
      ;;
    *) info "Skipping master" ;;
  esac

  echo ""
  info "Step 8/8: Verifying credentials..."
  if [ -d "$HOME/.password-store/kordinate" ]; then
    local placeholder_count=0 key val
    for key in tailscale/api_key tailscale/auth_key_gateway grafana_admin/api_key; do
      if pass show "kordinate/$key" &>/dev/null; then
        val=$(pass show "kordinate/$key" 2>/dev/null)
        if [ "$val" = "PLACEHOLDER" ]; then
          ((placeholder_count++)) || true
        fi
      fi
    done
    if [ "$placeholder_count" -gt 0 ]; then
      warn "$placeholder_count key(s) still have PLACEHOLDER values"
      echo "  Set real keys: pass edit kordinate/<service>/<key>"
    else
      log "Credentials configured"
    fi
    cmd_hydrate || warn "hydrate failed — run: ./setup.sh hydrate"
  else
    warn "Pass store not initialized — run: ./setup.sh profile"
  fi

  echo ""
  info "Running doctor to verify..."
  "$CLAUDE_HOME/setup/doctor.sh" --category connectivity || true

  echo ""
  log "Bootstrap complete!"
}

cmd_bootstrap() {
  local SUBCMD="${1:-}"

  bootstrap_usage() {
    echo "Usage: ./setup.sh bootstrap <command>"
    echo ""
    echo "Commands:"
    echo "  status     Show cluster setup status"
    echo "  cluster    Install k3s on a node"
    echo "  rbac       Bootstrap agent RBAC"
    echo "  gateway    Deploy Tailscale + monitoring gateway"
    echo "  master     Deploy master manifests (Grafana, workstation)"
    echo "  platform   Apply user additions from profile"
    echo "  full       End-to-end guided setup"
  }

  case "$SUBCMD" in
    status)   bootstrap_status ;;
    cluster)  bootstrap_cluster "${@:2}" ;;
    rbac)     bootstrap_rbac ;;
    gateway)  bootstrap_gateway ;;
    master)   bootstrap_master ;;
    platform) bootstrap_platform ;;
    full)     bootstrap_full ;;
    "")       bootstrap_usage; exit 0 ;;
    *)        err "Unknown command: $SUBCMD"; bootstrap_usage; exit 1 ;;
  esac
}

# ═══════════════════════════════════════════════════════════════
# MAIN DISPATCHER
# ═══════════════════════════════════════════════════════════════
usage() {
  echo "Usage: ./setup.sh <command>"
  echo ""
  echo "Commands:"
  echo "  link <url>  Link ~/.claude to an existing kordinate repo"
  echo "  init [name] Create a new private kordinate repo"
  echo "  profile     Scaffold config + initialize pass store"
  echo "  hydrate     Generate .mcp.json from config.yaml + pass"
  echo "  shell       PATH, tmux, claude alias → shell RC"
  echo "  doctor      Check prerequisites, profile, connectivity"
  echo "  bootstrap   Orchestrate cluster setup from scratch"
  echo "  export      Bundle profile + keys → encrypted archive"
  echo "  import      Restore from encrypted archive"
  echo "  uninstall   Remove shell config"
  echo "  client      SSH config for remote workstation access"
}

# ─── LINK — attach ~/.claude to an existing kordinate repo ───
cmd_link() {
  local REPO_URL="$1"
  if [ -z "$REPO_URL" ]; then
    err "Usage: ./setup.sh link <repo-url>"
    exit 1
  fi

  log "Linking ~/.claude to $REPO_URL"

  if [ -d "$CLAUDE_HOME/.git" ]; then
    # Already a git repo — just update remote
    local CURRENT_REMOTE
    CURRENT_REMOTE=$(git -C "$CLAUDE_HOME" remote get-url origin 2>/dev/null || true)
    if [ "$CURRENT_REMOTE" = "$REPO_URL" ]; then
      info "Already linked to $REPO_URL"
    else
      git -C "$CLAUDE_HOME" remote set-url origin "$REPO_URL"
      log "Updated remote to $REPO_URL"
    fi
    git -C "$CLAUDE_HOME" pull --rebase origin main || true
  else
    # Clone into ~/.claude (must be empty or non-existent)
    if [ -d "$CLAUDE_HOME" ] && [ "$(ls -A "$CLAUDE_HOME" 2>/dev/null)" ]; then
      err "~/.claude exists and is not empty. Back it up first."
      exit 1
    fi
    git clone "$REPO_URL" "$CLAUDE_HOME"
  fi

  # Verify it's a kordinate repo
  if [ ! -f "$CLAUDE_HOME/CLAUDE.md" ] || [ ! -d "$CLAUDE_HOME/agents" ]; then
    err "Not a kordinate repo (missing CLAUDE.md or agents/)"
    exit 1
  fi
  log "Verified kordinate repo structure"

  # Pass keyring path
  read -rp "Pass keyring path [~/.password-store]: " PASS_DIR
  PASS_DIR="${PASS_DIR:-$HOME/.password-store}"
  export PASSWORD_STORE_DIR="$PASS_DIR"

  if [ -d "$PASS_DIR" ]; then
    log "Using existing pass store at $PASS_DIR"
    # Verify we can read it
    if ! pass ls kordinate/ >/dev/null 2>&1; then
      warn "Cannot read pass store — check GPG key"
    fi
  else
    warn "Pass store not found at $PASS_DIR — run './setup.sh profile' to initialize"
  fi

  # Hydrate
  cmd_hydrate
  log "Link complete. Run './setup.sh doctor' to verify."
}

# ─── INIT — create a new private kordinate repo ───
cmd_init() {
  local REPO_NAME="${1:-kordinate}"

  log "Initializing new kordinate repo: $REPO_NAME"

  # Check gh is available
  if ! command -v gh >/dev/null 2>&1; then
    err "gh (GitHub CLI) is required. Install: https://cli.github.com/"
    exit 1
  fi

  # Check gh auth
  if ! gh auth status >/dev/null 2>&1; then
    err "Not authenticated with GitHub. Run: gh auth login"
    exit 1
  fi

  # Create private repo
  local GH_USER
  GH_USER=$(gh api user -q .login)
  local REPO_FULL="${GH_USER}/${REPO_NAME}"

  if gh repo view "$REPO_FULL" >/dev/null 2>&1; then
    warn "Repo $REPO_FULL already exists"
  else
    gh repo create "$REPO_NAME" --private --confirm
    log "Created private repo: $REPO_FULL"
  fi

  # Init ~/.claude as git repo if needed
  if [ ! -d "$CLAUDE_HOME/.git" ]; then
    git -C "$CLAUDE_HOME" init
    git -C "$CLAUDE_HOME" remote add origin "https://github.com/${REPO_FULL}.git"
  else
    git -C "$CLAUDE_HOME" remote set-url origin "https://github.com/${REPO_FULL}.git"
  fi

  # GPG key for pass
  if ! gpg --list-keys 2>/dev/null | grep -q uid; then
    log "Generating GPG key for pass encryption..."
    gpg --batch --gen-key <<GPGEOF
%no-protection
Key-Type: RSA
Key-Length: 4096
Name-Real: kordinate
Name-Email: kordinate@localhost
Expire-Date: 0
%commit
GPGEOF
    log "GPG key generated"
  fi

  # Pass keyring path
  read -rp "Pass keyring path [~/.password-store]: " PASS_DIR
  PASS_DIR="${PASS_DIR:-$HOME/.password-store}"
  export PASSWORD_STORE_DIR="$PASS_DIR"

  # Init pass store
  local GPG_ID
  GPG_ID=$(gpg --list-keys --with-colons 2>/dev/null | grep '^uid' | head -1 | cut -d: -f10)
  if [ ! -d "$PASS_DIR" ]; then
    pass init "$GPG_ID"
    log "Initialized pass store at $PASS_DIR"
  fi

  # Scaffold config
  if [ ! -f "$CLAUDE_HOME/config.yaml" ]; then
    cp "$CLAUDE_HOME/config.yaml.template" "$CLAUDE_HOME/config.yaml"
    log "Created config.yaml from template — edit with real values"
  fi

  # Initial commit + push
  git -C "$CLAUDE_HOME" add -A
  git -C "$CLAUDE_HOME" commit -m "initial kordinate setup" || true
  git -C "$CLAUDE_HOME" push -u origin main || git -C "$CLAUDE_HOME" push -u origin HEAD:main

  log "Init complete. Edit config.yaml, then run './setup.sh profile' to populate credentials."
}

if [ -z "$CMD" ]; then
  usage
  exit 0
fi

echo "kordinate ($CMD)"
echo ""

case "$CMD" in
  link)       cmd_link "${@:2}" ;;
  init)       cmd_init "${@:2}" ;;
  profile)    cmd_profile ;;
  hydrate)    cmd_hydrate ;;
  shell)      cmd_shell ;;
  doctor)     exec "$CLAUDE_HOME/setup/doctor.sh" "${@:2}" ;;
  bootstrap)  cmd_bootstrap "${@:2}" ;;
  export)     cmd_export "${@:2}" ;;
  import)     cmd_import "${@:2}" ;;
  uninstall)  exec "$CLAUDE_HOME/setup/uninstall.sh" ;;
  client)     cmd_client ;;
  *) usage; exit 1 ;;
esac
