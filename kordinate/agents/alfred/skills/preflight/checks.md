---
name: preflight-checks
description: Full registry of all preflight validation checks -- config, overlays, credentials, manifests, network
level: 3
---

# Preflight Check Registry

Complete list of all checks performed by `/preflight`. Each check reports `[pass]` or `[FAIL]` with a detail message.

## 1. Config Validity

| # | Check | Validation | Fix |
|---|-------|-----------|-----|
| C1 | config.yaml exists | `$KORDINATE_HOME/profile/config.yaml` must exist | Create the config file with `/config add-cluster` |
| C2 | Valid YAML | File must parse as valid YAML | Fix syntax errors in config.yaml |
| C3 | Required fields present | Each cluster must have: `name`, `description`, `tailscale_ip`, `gateway_tailscale_ip`, `nodes`, `namespaces`, `manifests.gateway`, `manifests.bootstrap` | Add missing fields with `/config update` |
| C4 | IPs valid | `tailscale_ip`, `gateway_tailscale_ip`, each `nodes[]` entry, and optional `gateway_lan_ip` must be valid IPv4 (four octets, 0-255) | Correct the IP address in config |
| C5 | Ports valid | `services.<name>.port` must be an integer in range 1-65535 | Update the port value with `/config update` |
| C6 | Manifest paths exist | `manifests.gateway` and `manifests.bootstrap` (and any optional manifest paths) must reference existing directories under `$KORDINATE_HOME/` | Create the directory or fix the path |
| C7 | At least one node | `nodes` list must contain at least one entry | Add node IPs to the cluster config |
| C8 | Gateway namespace | `namespaces` list must include `gateway` | Add `gateway` to the namespaces list |
| C9 | LAN network CIDR | If `lan_network` is present, it must be valid CIDR notation (e.g., `10.95.43.0/24`) | Fix the CIDR value |

## 2. Overlay Readiness

| # | Check | Validation | Fix |
|---|-------|-----------|-----|
| O1 | Overlay directory exists | `$KORDINATE_HOME/profile/overlays/<cluster>/` must exist | Run `/bootstrap generate-overlays <cluster>` |
| O2 | Gateway overlay present | `<overlay-dir>/gateway/` must exist | Run `/bootstrap generate-overlays <cluster>` |
| O3 | Namespace overlays present | For each namespace in config `namespaces` list, a matching overlay directory must exist | Run `/bootstrap generate-overlays <cluster>` |
| O4 | No config drift | Overlay values (IPs, ports, namespaces) must match current config.yaml | Run `/bootstrap generate-overlays <cluster>` to regenerate |
| O5 | kustomization.yaml valid | Each namespace overlay directory must contain a `kustomization.yaml` | Run `/bootstrap generate-overlays <cluster>` |
| O6 | Base path references | `kustomization.yaml` `resources` entries must point to existing base manifest directories | Fix base path references in kustomization.yaml |

## 3. Credential Availability

The authoritative list of required credentials is the keys registry at [keys/registry.md](../keys/registry.md). The checks below mirror that registry's required entries. If the registry is updated, this table must be updated to match.

| # | Check | Pass entry | Required | Readers |
|---|-------|-----------|----------|---------|
| K1 | GitHub token | `kordinate/github/token` | yes | installer, scribe |
| K2 | Tailscale workstation auth | `kordinate/tailscale/auth_key_workstation` | yes | workstation entrypoint |
| K3 | Tailscale gateway auth | `kordinate/tailscale/auth_key_gateway` | yes (per cluster) | deploy-cluster |
| K4 | Tailscale API key | `kordinate/tailscale/api_key` | yes | workstation entrypoint |
| K5 | SSH authorized key | `kordinate/ssh/authorized_key` | yes | workstation entrypoint |
| K6 | SSH password | `kordinate/ssh/password` | yes | workstation entrypoint |
| K7 | MinIO root user | `kordinate/minio/root_user` | yes (per cluster) | deploy-cluster |
| K8 | MinIO root password | `kordinate/minio/root_password` | yes (per cluster) | deploy-cluster |
| K9 | Cloudflare tunnel token | `kordinate/cloudflare/tunnel_token` | yes | deploy-cluster, migrate |
| K10 | Grafana admin password | `kordinate/grafana_admin/password` | yes | deploy-cluster |
| K11 | Grafana API key | `kordinate/grafana_admin/api_key` | yes | kord-hydrate, auth-check |
| K12 | Claude credentials | `kordinate/claude/credentials` | yes | installer, beorn entrypoint |

### GPG Check

| # | Check | Validation | Fix |
|---|-------|-----------|-----|
| K0 | Pass store initialized | `gpg --list-keys` must succeed and `~/.password-store/` must exist | Initialize with `pass init <gpg-id>` |

### Credential Verification Method

For each credential, verify existence with:
```
pass ls kordinate/<service>/<key> 2>&1
```

**Never use `pass show`** -- existence check only, never display values.

## 4. Manifest Validity

| # | Check | Validation | Fix |
|---|-------|-----------|-----|
| M1 | Base directories exist | Each path in `manifests.*` must be an existing directory | Create the directory or fix the config path |
| M2 | kustomization.yaml present | Each base manifest directory must contain `kustomization.yaml` | Add the missing kustomization.yaml |
| M3 | No placeholder values | Overlay patches must not contain `MUST_BE_SET_BY_OVERLAY` | Set the actual value in the overlay patch |
| M4 | No REGISTRY placeholders | Overlay patches must not contain unresolved `REGISTRY` tokens | Replace with actual registry URL in the overlay |

### Placeholder Scan Method

Search overlay files for unresolved tokens:
```
grep -r 'MUST_BE_SET_BY_OVERLAY\|REGISTRY' <overlay-dir>/
```

Any match is a FAIL with the file path and line number reported.

## 5. Network Reachability (opt-in: `--net`)

| # | Check | Validation | Fix |
|---|-------|-----------|-----|
| N1 | Tailscale IP reachable | `ping -c 1 -W 3 <tailscale_ip>` succeeds | Check Tailscale status, ensure node is online |
| N2 | Gateway IP reachable | `ping -c 1 -W 3 <gateway_tailscale_ip>` succeeds | Check Tailscale status, ensure gateway is online |
| N3 | Node IPs reachable | `ssh -o ConnectTimeout=5 -o BatchMode=yes <node_ip> exit` succeeds for each node | Verify SSH config and node availability |
| N4 | Registry accessible | HTTP GET to registry URL returns 200 | Check registry deployment and network path |

Network checks are skipped by default. Pass `--net` to enable. When skipped, the output shows:
```
NETWORK (skipped -- use --net to enable)
```

## Check Execution Order

Checks run in dependency order:

1. **Config** -- everything depends on config being valid
2. **Overlays** -- depend on config for expected namespaces and paths
3. **Credentials** -- independent but listed after config for readability
4. **Manifests** -- depend on config for manifest paths
5. **Network** -- depends on config for IPs, opt-in only

If Config checks fail critically (file missing or unparseable YAML), subsequent checks that depend on config values are skipped with a note:
```
OVERLAYS (skipped -- config invalid)
```

## Summary Logic

- Count total `[pass]` and `[FAIL]` results across all categories.
- If any `[FAIL]`: verdict is `NOT READY` with a `Fix:` line listing remediation steps.
- If all `[pass]`: verdict is `READY`.
- Skipped categories (network without `--net`, or categories skipped due to config failure) do not count toward pass/fail totals.
