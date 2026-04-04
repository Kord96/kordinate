# Storage Paths

Level 3 resource for get and store skills. Maps each domain to its storage location.

| Domain | Path | Format | Notes |
|--------|------|--------|-------|
| config | `$KORDINATE_HOME/profile/config.yaml` | YAML | Validate: required fields (name, nodes, namespaces), valid IPs, valid ports |
| keys | `pass store` at `kordinate/` prefix | GPG-encrypted | Access via `pass show <path>`, insert via `pass insert -f <path>`. Never write plaintext. |
| profiles | `$KORDINATE_HOME/profile/model-profiles.yaml` | YAML | Alfred-managed source of truth for reusable LLM/backend profile definitions |
| overlays | `$KORDINATE_HOME/profile/overlays/<cluster>/<namespace>/` | Kustomize dirs | Each namespace has a `kustomization.yaml`. Created by charon, stored by alfred. |
| platform | `$KORDINATE_HOME/profile/overlays/platform/<env>/` | Kustomize dirs | Per-environment agent pod scaling and resource limits. Created by charon, stored/validated/updated by alfred. |
}},{
## Platform overlay contents

Each environment directory under `profile/overlays/platform/<env>/` contains:

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
