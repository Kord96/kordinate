# Alfred Key Paths

Common pass-store entries under `kordinate/`:

- `github/token`
- `tailscale/auth_key_workstation`
- `tailscale/auth_key_gateway`
- `tailscale/api_key`
- `ssh/authorized_key`
- `ssh/password`
- `minio/root_user`
- `minio/root_password`
- `cloudflare/tunnel_token`
- `grafana_admin/password`
- `grafana_admin/api_key`
- `claude/credentials`

Rules:
- treat these as examples and stable conventions, not an exhaustive list
- write secrets only through `pass`
- never echo secret values in normal status output
