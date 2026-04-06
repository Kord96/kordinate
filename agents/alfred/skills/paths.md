# Storage Paths

Level 3 resource for get and store skills. Maps each domain to its storage location.

| Domain | Path | Format | Notes |
|--------|------|--------|-------|
| config | `$KORDINATE_HOME/agents/alfred/profile/config.yaml` | YAML | Alfred-owned source of truth. Validate: required fields (name, nodes, namespaces), valid IPs, valid ports |
| keys | `pass store` at `kordinate/` prefix | GPG-encrypted | Access via `pass show <path>`, insert via `pass insert -f <path>`. Never write plaintext. |
| profiles | `$KORDINATE_HOME/agents/alfred/profile/model-profiles.yaml` | YAML | Alfred-owned source of truth for reusable LLM/backend profile definitions |
| overlays | `$KORDINATE_HOME/agents/alfred/profile/overlays/<cluster>/<namespace>/` | Kustomize dirs | Alfred-owned source of truth for generated overlays. |
| platform | `$KORDINATE_HOME/agents/alfred/profile/overlays/platform/<env>/` | Kustomize dirs | Alfred-owned source of truth for per-environment agent runtime scaling and resources. |
| runtime projection | `$KORDINATE_HOME/shared/runtime/profile/` | Mixed | Read-only projection published from Alfred-owned source via `shared/scripts/publish-profile.sh` for bootstrap/runtime consumers |
}},{
## Platform overlay contents

Each environment directory under `agents/alfred/profile/overlays/platform/<env>/` contains:

- `kustomization.yaml` — Kustomize entry point; references scaling.yaml and resources.yaml as patches.
- `scaling.yaml` — KEDA ScaledObject parameters per agent: minReplicaCount, maxReplicaCount, cooldownPeriod, and trigger thresholds.
- `resources.yaml` — Kubernetes resource limits and requests per agent pod (cpu, memory).

## Config required fields

When validating config on store:
- `name`, `description`, `tailscale_ip`, `gateway_tailscale_ip` (strings)
- `nodes` (list, at least one)
- `namespaces` (list, must include `gateway`)
- `services.<name>.port` — integers in 1-65535

## Key paths

Standard keys under `kordinate/`:
- `github/token`
- `tailscale/auth_key_workstation`, `tailscale/auth_key_gateway`, `tailscale/api_key`
- `ssh/authorized_key`, `ssh/password`
- `minio/root_user`, `minio/root_password`
- `cloudflare/tunnel_token`
- `grafana_admin/password`, `grafana_admin/api_key`
- `claude/credentials`
