---
name: preflight
description: Check all prerequisites before deployment -- config, overlays, secrets
curated: true
scope: global
---

`/preflight [cluster] [--net]`

Run all prerequisite checks before a deployment. If no cluster specified, check all clusters.

This is the pre-deploy gate -- deployer should call this (or be advised to call this) before any `/infra bootstrap` or `/infra roll`.

## Arguments

`$ARGUMENTS` -- Optional cluster name. If omitted, checks all clusters in config.

Optional flags:
- `--net` -- enable network reachability checks (requires cluster access)

## Procedure

1. Parse arguments: extract cluster name (optional) and flags (`--net`) from `$ARGUMENTS`.
2. Read `$KORDINATE_HOME/profile/config.yaml`.
3. If a cluster is specified, check only that cluster. Otherwise iterate all clusters.
4. Run checks in order: config -> overlays -> credentials -> manifests -> network (if `--net`).
5. For each check, report pass/fail with details.
6. Summary at end with overall READY / NOT READY verdict.

### Step 1: Config Validity

1. Verify `$KORDINATE_HOME/profile/config.yaml` exists and is valid YAML.
2. For each target cluster, validate all required fields are present:
   - `name`, `description`, `tailscale_ip`, `gateway_tailscale_ip` (strings)
   - `nodes` (list, at least one entry)
   - `namespaces` (list, must include `gateway`)
   - `manifests.gateway`, `manifests.bootstrap` (strings, required paths)
3. Validate IPs match IPv4 format (`tailscale_ip`, `gateway_tailscale_ip`, each `nodes` entry, optional `gateway_lan_ip`).
4. Validate `services.<name>.port` values are integers in range 1-65535.
5. Check manifest paths reference existing directories under `$KORDINATE_HOME/`.
6. Verify at least one node is defined.

### Step 2: Overlay Readiness

1. Verify overlay directory exists at `$KORDINATE_HOME/profile/overlays/<cluster>/`.
2. Verify all namespace overlays are present (`gateway/` required; `monitor/`, `master/` per config namespaces).
3. Check overlays match current config -- look for drift (IPs, ports, namespaces that have diverged).
4. Verify each namespace overlay contains a `kustomization.yaml` that references valid base paths.

### Step 3: Credential Availability

1. Verify the pass store is initialized and a GPG key is available (`gpg --list-keys` succeeds).
2. Check all required pass entries exist (from the keys registry at [keys/registry.md](../keys/registry.md)):
   - `kordinate/github/token`
   - `kordinate/tailscale/auth_key_workstation`
   - `kordinate/tailscale/auth_key_gateway`
   - `kordinate/tailscale/api_key`
   - `kordinate/ssh/authorized_key`
   - `kordinate/ssh/password`
   - `kordinate/minio/root_user`
   - `kordinate/minio/root_password`
   - `kordinate/cloudflare/tunnel_token`
   - `kordinate/grafana_admin/password`
   - `kordinate/grafana_admin/api_key`
   - `kordinate/claude/credentials`
3. For each entry, run `pass ls kordinate/<service>/<key>` to verify existence. **Never display values.**

### Step 4: Manifest Validity

1. For each manifest path in config (`manifests.gateway`, `manifests.bootstrap`, and any optional `manifests.monitor`, `manifests.master`, `manifests.platform`), verify the directory exists.
2. Verify each base manifest directory contains a `kustomization.yaml`.
3. Scan overlay patches for placeholder values: flag any occurrence of `MUST_BE_SET_BY_OVERLAY`, `REGISTRY`, or similar unresolved tokens.

### Step 5: Network Reachability (only with `--net`)

1. Ping Tailscale IPs (`tailscale_ip`, `gateway_tailscale_ip`) for each cluster.
2. Test SSH reachability to each node IP.
3. Check registry URL is accessible (if defined in config).

## Output Format

```
Preflight: <cluster> (<date>)

CONFIG
  [pass] config.yaml exists and valid
  [pass] Required fields present
  [pass] IPs valid
  [FAIL] Port 99999 out of range for services.postgres.port

OVERLAYS
  [pass] Overlay directory exists
  [pass] gateway/ overlay present
  [FAIL] monitor/ overlay missing
  [pass] No drift detected

CREDENTIALS
  [pass] 11/12 required keys present
  [FAIL] Missing: kordinate/grafana_admin/api_key

MANIFESTS
  [pass] Base manifest directories exist
  [pass] No unresolved placeholders

NETWORK (skipped -- use --net to enable)

Summary: 11 passed, 2 failed -- NOT READY
  Fix: add monitor overlay, add grafana_admin/api_key to pass store
```

When all checks pass:

```
Summary: 13 passed, 0 failed -- READY
```

## Important Notes

- This is a read-only operation -- preflight never modifies anything.
- It combines checks from `/config validate`, `/overlay validate`, and `/keys audit` into one unified view. The credential list comes from the keys registry ([keys/registry.md](../keys/registry.md)).
- Network checks are opt-in because they require cluster access.
- The goal is to catch issues BEFORE deployer starts a deployment.
- Exit with clear "READY" or "NOT READY" verdict.
- Alfred never deploys -- after identifying failures, advise which commands to run to fix them.
- Use `$KORDINATE_HOME` to reference the kordinate root (resolves to `/kord/kordinate` at runtime).

## Resources

- [checks.md](checks.md) -- full check registry with all validations (Level 3)
