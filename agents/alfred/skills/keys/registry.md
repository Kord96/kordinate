---
name: keys-registry
description: Canonical pass store schema -- required keys, readers, and per-cluster expectations
curated: true
scope: global
---

# Pass Store Registry

Canonical list of credentials under `kordinate/` in the pass store. This file is the source of truth for `/keys audit` and `/keys list`.

## Schema

```
kordinate/
├── github/
│   └── token              # required — GitHub API access
│                           # readers: installer, scribe
├── tailscale/
│   ├── auth_key_workstation  # required — workstation pod Tailscale auth
│   │                          # readers: workstation entrypoint
│   ├── auth_key_gateway      # required per cluster — gateway Tailscale auth
│   │                          # readers: deploy-cluster
│   └── api_key               # required — Tailscale API for cleanup
│                              # readers: workstation entrypoint
├── ssh/
│   ├── authorized_key     # required — SSH public key for workstation
│   │                       # readers: workstation entrypoint
│   └── password            # required — SSH password for workstation
│                            # readers: workstation entrypoint
├── minio/
│   ├── root_user           # required per cluster — MinIO admin user
│   │                        # readers: deploy-cluster
│   └── root_password       # required per cluster — MinIO admin password
│                            # readers: deploy-cluster
├── cloudflare/
│   ├── tunnel_token        # required — Cloudflare tunnel token
│   │                        # readers: deploy-cluster, migrate
│   └── api_token           # optional — Cloudflare API token
│                            # readers: auth-check
├── grafana_admin/
│   ├── password            # required — Grafana admin password
│   │                        # readers: deploy-cluster
│   └── api_key             # required — Grafana API key for MCP
│                            # readers: kord-hydrate, auth-check
└── claude/
    └── credentials         # required — Claude API credentials JSON
                             # readers: installer, beorn entrypoint
```

## Key Table

| Path | Required | Per-Cluster | Readers | Notes |
|------|----------|-------------|---------|-------|
| `github/token` | yes | no | installer, scribe | GitHub API PAT |
| `tailscale/auth_key_workstation` | yes | no | workstation entrypoint | Tailscale auth for workstation pod |
| `tailscale/auth_key_gateway` | yes | yes | deploy-cluster | One per cluster gateway |
| `tailscale/api_key` | yes | no | workstation entrypoint | Used for Tailscale node cleanup |
| `ssh/authorized_key` | yes | no | workstation entrypoint | SSH public key |
| `ssh/password` | yes | no | workstation entrypoint | SSH login password |
| `minio/root_user` | yes | yes | deploy-cluster | MinIO admin username |
| `minio/root_password` | yes | yes | deploy-cluster | MinIO admin password |
| `cloudflare/tunnel_token` | yes | no | deploy-cluster, migrate | Cloudflare tunnel auth |
| `cloudflare/api_token` | no | no | auth-check | Cloudflare API access |
| `grafana_admin/password` | yes | no | deploy-cluster | Grafana admin login |
| `grafana_admin/api_key` | yes | no | kord-hydrate, auth-check | Grafana MCP API key |
| `claude/credentials` | yes | no | installer, beorn entrypoint | Claude API credentials JSON blob |

## Per-Cluster Keys

When `$KORDINATE_HOME/profile/config.yaml` defines multiple clusters, the following keys should exist for **each** cluster. The audit procedure checks that at least one instance exists; it does not enforce per-cluster naming since the current convention uses a single shared entry.

- `tailscale/auth_key_gateway`
- `minio/root_user`
- `minio/root_password`

## Naming Convention

All entries must follow:

- **Structure**: `kordinate/<service>/<key>` (exactly 3 path segments)
- **Characters**: lowercase alphanumeric and underscores only
- **No spaces, no uppercase, no special characters** beyond `_`
- **Max depth**: 3 levels (`kordinate/service/key`)
