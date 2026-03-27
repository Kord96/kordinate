---
name: config-schema
description: Schema reference for profile/config.yaml — required fields, types, and structure
level: 3
---

# config.yaml Schema

This document defines the expected structure, required fields, types, and defaults for `$KORDINATE_HOME/profile/config.yaml`.

## Top-Level Structure

```yaml
clusters:       # required — at least one cluster
network:        # required — network/tailnet config
cloudflare:     # optional — tunnel and domain config
node_hostnames: # optional — hostname-to-IP mapping
```

## clusters

Each key under `clusters` is a cluster name. At least one cluster must be defined.

```yaml
clusters:
  <cluster-name>:
    name: string                     # required — must match the key
    description: string              # required
    tailscale_ip: string             # required — Tailscale IP of control plane (IPv4)
    gateway_tailscale_ip: string     # required — Tailscale IP of gateway node (IPv4)
    lan_network: string              # optional — CIDR notation (e.g., 10.95.43.0/24)
    gateway_lan_ip: string           # optional — LAN IP of gateway (IPv4)
    nodes: [string]                  # required — at least one node IP (IPv4)
    namespaces: [string]             # required — at least [gateway]
    manifests:                       # required
      gateway: string                # required — path to gateway manifests
      bootstrap: string              # required — path to bootstrap manifests
      monitor: string                # optional — path to monitor manifests
      master: string                 # optional — path to master manifests
      platform: string               # optional — path to platform additions
    workloads: [string]              # optional — project names deployed here
    services:                        # optional — service endpoints
      <service-name>:
        port: integer                # required for each service (1-65535)
        host: string                 # optional
        url: string                  # optional
        user: string                 # optional (e.g., postgres user)
        database: string             # optional (e.g., postgres database)
        namespace: string            # optional (e.g., grafana namespace)
```

### Cluster Field Validation

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `name` | string | yes | Must match the cluster key |
| `description` | string | yes | Non-empty |
| `tailscale_ip` | string | yes | Valid IPv4 |
| `gateway_tailscale_ip` | string | yes | Valid IPv4 |
| `lan_network` | string | no | Valid CIDR (x.x.x.x/n) |
| `gateway_lan_ip` | string | no | Valid IPv4 |
| `nodes` | list | yes | At least one valid IPv4 |
| `namespaces` | list | yes | At least one entry; must include `gateway` |
| `manifests.gateway` | string | yes | Existing directory path |
| `manifests.bootstrap` | string | yes | Existing directory path |
| `manifests.monitor` | string | no | Existing directory path if set |
| `manifests.master` | string | no | Existing directory path if set |
| `manifests.platform` | string | no | Existing directory path if set |
| `workloads` | list | no | List of strings |
| `services.<name>.port` | integer | yes (per service) | 1-65535 |

## network

```yaml
network:
  tailnet: string              # required — Tailscale tailnet domain
  grafana_public: string       # optional — public Grafana domain
  docs_public: string          # optional — public docs domain
```

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `tailnet` | string | yes | Non-empty domain string |
| `grafana_public` | string | no | Valid domain |
| `docs_public` | string | no | Valid domain |

## cloudflare

```yaml
cloudflare:
  account_id: string           # optional
  tunnel_id: string            # optional
  tunnel_name: string          # optional
  domains: [string]            # optional — list of managed domains
```

All fields are optional. If the `cloudflare` section is present, no fields are individually required.

## node_hostnames

```yaml
node_hostnames:
  <hostname>: string           # IP address mapping
```

A flat map of hostname to IP address. All values should be valid IPv4 addresses. This section is optional.
