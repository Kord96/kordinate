# profile/

Site-specific configuration. Everything here is gitignored except this file.

## Layout

```
profile/
├── config.yaml             # Cluster IPs, ports, services, registry
├── topology.yaml           # App definitions, monitoring, health thresholds
├── mcp.json                # MCP server config (symlinked from ../.mcp.json)
├── locks/                  # Agent auth locks (deployer, sauron, scribe)
├── keystore/               # Symlink → ~/.password-store/kordinate/
├── additions/              # Extra k8s manifests applied to clusters
├── overlays/               # Kustomize overlays per cluster/environment
└── README.md               # This file
```

## Setup

```bash
# Create config from the template comments in kordinate script, or:
cp /dev/null profile/config.yaml
# Edit with your cluster details (see config structure below)

# Generate MCP server config from config.yaml + pass store
./kordinate hydrate

# Agent auth locks are generated during bootstrap
# Pass keystore is set up via ./kordinate init or ./kordinate import
```

## config.yaml structure

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

## topology.yaml structure

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
