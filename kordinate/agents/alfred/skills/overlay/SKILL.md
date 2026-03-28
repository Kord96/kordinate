---
name: overlay
description: Validate, diff, and regenerate kustomize overlays
curated: true
scope: global
---

Validate, diff, and regenerate kustomize overlays against profile/config.yaml. $ARGUMENTS should include the subcommand and any arguments.

## Subcommands

| Subcommand | Purpose |
|-----------|---------|
| `validate <cluster>` | Check overlays match config.yaml -- no drift |
| `diff <cluster>` | Show what would change if overlays were regenerated |
| `status` | Show overlay status for all clusters -- up-to-date, stale, missing |
| `regenerate <cluster>` | Regenerate overlays from config (delegates to deployer) |

## Procedure: `validate`

1. Read `$KORDINATE_HOME/profile/config.yaml`.
2. Find the target cluster config under `clusters.<name>`.
3. Check overlay directory exists at `$KORDINATE_HOME/profile/overlays/<cluster>/`.
4. For each namespace overlay directory (gateway, monitor, master):
   - Read `patches.yaml`.
   - Extract values that should come from config:
     - Registry URL (`clusters.<name>.services.registry.url` -> `REGISTRY` in patches)
     - Cluster name (`clusters.<name>.name` -> Tailscale hostname / `MUST_BE_SET_BY_OVERLAY`)
     - Tailscale IPs (`clusters.<name>.gateway_tailscale_ip` -> alloy-config, gateway-registry)
     - Domain references (`network.grafana_public` -> domain fields in patches)
     - Storage class (`longhorn` -> PVC storage class in patches)
   - Compare against current config.yaml values.
   - Flag any mismatches as "drift".
5. For generated ConfigMaps (alloy-config, gateway-registry) in master namespace:
   - Check they reference all current clusters from config.
   - Flag missing or extra cluster references.
6. Report: valid (in sync) or list of drift items with locations.

## Procedure: `diff`

1. Run validate internally to find drift.
2. For each drifted value, show:
   ```
   <file>: <field>
     overlay: <current overlay value>
     config:  <current config value>
   ```
3. If no drift: "Overlays are up-to-date with config.yaml"

## Procedure: `status`

1. Read `$KORDINATE_HOME/profile/config.yaml` for all cluster names.
2. For each cluster:
   - Check if overlay directory exists at `$KORDINATE_HOME/profile/overlays/<cluster>/` -> missing or present.
   - If present, run validate -> up-to-date or stale.
3. Report table:
   ```
   Cluster      Status
   vandc        up-to-date
   home         stale (2 drift items)
   newcluster   missing
   ```

## Procedure: `regenerate`

1. Run validate first to confirm what will change.
2. Show the diff so the user sees what is out of sync.
3. Delegate to deployer: `/kord deployer generate overlays for <cluster>`.
4. After generation completes, run validate again to confirm sync.
5. Report result: success (now in sync) or remaining drift items.

## Important Notes

- Alfred validates and diffs -- deployer generates. Never write overlay files directly.
- Overlay paths: `$KORDINATE_HOME/profile/overlays/<cluster>/`.
- Base manifest paths: referenced in config.yaml under `clusters.<name>.manifests`.
- Secrets are NOT in overlays -- they are created at deploy time from `pass`.
- If config.yaml changes, overlays become stale until regenerated.
- The `regenerate` subcommand is a delegation -- alfred identifies the drift, deployer does the actual file generation.

## Resources

- [overlay-structure.md](overlay-structure.md) -- Overlay directory structure and config mapping reference (Level 3)
