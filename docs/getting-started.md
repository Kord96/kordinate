# Getting Started

How to install, configure, and link kordinate to Claude Code.

## Profile

Site-specific configuration lives in `profile/`. Everything is git-crypt encrypted except locks, keybindings, and README.md.

```
profile/
├── config.yaml             # Cluster IPs, ports, services, registry
├── topology.yaml           # App definitions, monitoring, health thresholds
├── mcp.json                # MCP server config
├── keybindings.json        # Keyboard shortcuts
├── locks/                  # Agent auth locks (deployer, sauron, scribe)
├── keystore/               # Symlink → ~/.password-store/kordinate/
├── additions/              # Extra k8s manifests applied to clusters
└── overlays/               # Kustomize overlays per cluster/environment
```

### Setup

```bash
# Create config with your cluster details
cp /dev/null profile/config.yaml
# Edit — see config.yaml structure below

# Generate MCP server config from config.yaml + pass store
./installer/kordinate-cli hydrate

# Agent auth locks are generated during bootstrap
# Pass keystore is set up via ./kordinate init or ./kordinate import
```

### config.yaml

```yaml
clusters:
  mycluster:
    name: mycluster
    tailscale_ip: 100.x.x.x
    lan_network: 10.0.0.0/24
    gateway_lan_ip: 10.0.0.1
    nodes: [10.0.0.1, 10.0.0.2]
    namespaces: [dev, test, prod, monitor]
    manifests:
      master: agents/deployer/manifests/master
      monitor: agents/deployer/manifests/monitor
      bootstrap: agents/deployer/manifests/bootstrap
      platform: profile/additions
    services:
      postgres: { port: 30632, user: myuser, database: mydb }
      redis: { port: 30379 }
      metrics: { port: 30091 }
      grafana: { port: 30300, namespace: master }
      registry: { port: 5000, host: 10.0.0.1 }

network:
  tailnet: tailXXXXXX.ts.net
  grafana_public: grafana.example.com

cloudflare:
  account_id: ""
  tunnel_id: ""
  tunnel_name: ""
  domains: []
```

### topology.yaml

```yaml
apps:
  your-app:
    label: your-app
    namespaces: [dev, test, prod]
    consumers:
      component-a: { port: 9100 }

monitoring:
  retention:
    gateway: 3h
    master: 30d

health:
  sentinel:
    port: 9131
    interval: 30s

logging:
  suppress: [kafka, urllib3]
  format: json
```

## Link Mapping

Kordinate's framework lives in `~/kordinate/kordinate/`. Claude Code expects its files at `~/.claude/`. The linking layer (`installer/link.sh`) bridges them.

### Direct (same structure)

| Claude Code | Kordinate |
|-------------|-----------|
| `agents/` | `agents/` |
| `commands/` | `commands/` |

### Remapped (different location)

| Claude Code | Kordinate | Why different |
|-------------|-----------|---------------|
| `settings.json` | `settings.json` (framework root) | Framework config, not inside agents/ |
| `keybindings.json` | `profile/keybindings.json` | Site-specific |
| `.mcp.json` | `profile/mcp.json` | Site-specific, encrypted |
| `agent-memory/<agent>/` | `agents/<agent>/memory/dynamic/` | Memory colocated with agent, not separate tree |

### Renamed (different filename)

Kordinate uses `AGENT.md`, Claude Code expects `CLAUDE.md`. Copied on `link.sh deploy`, synced back on `link.sh sync`:

| Claude Code | Kordinate |
|-------------|-----------|
| `CLAUDE.md` | `agents/AGENT.md` |
| `agents/<agent>/CLAUDE.md` | `agents/<agent>/AGENT.md` |

### Kordinate-specific links

Not Claude Code conventions — linked so hooks and scripts resolve at stable paths:

| At `~/.claude/` | Kordinate | Used by |
|------------------|-----------|---------|
| `hooks/` | `hooks/` | `settings.json` references `$HOME/.claude/hooks/` |
| `profile/` | `profile/` | Hooks read locks at `profile/locks/` |

### External

| Link | Target | Purpose |
|------|--------|---------|
| `profile/keystore/` | `~/.password-store/kordinate/` | GPG credential store (`pass`) |
