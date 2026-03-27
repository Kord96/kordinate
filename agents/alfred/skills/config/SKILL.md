---
name: config
description: Validate, update, and diff profile/config.yaml
curated: true
scope: global
---

Validate, update, and diff the kordinate profile configuration. $ARGUMENTS should include the subcommand and any arguments.

## Subcommands

| Subcommand | Purpose |
|-----------|---------|
| `validate` | Validate config.yaml against schema -- required fields, types, structure |
| `show [cluster]` | Display current config (or a specific cluster's config) |
| `diff` | Show what changed in config.yaml vs the last overlay generation |
| `add-cluster <name>` | Add a new cluster entry with interactive prompts for required fields |
| `update <path> <value>` | Update a specific config value (e.g., `clusters.vandc.tailscale_ip 100.x.x.x`) |
| `schema` | Display the config.yaml schema -- what fields are required, types, defaults |

## Procedure: `validate`

1. Read `$KORDINATE_HOME/profile/config.yaml`.
2. Check all required fields exist for each cluster:
   - `name`, `description`, `tailscale_ip`, `gateway_tailscale_ip` (strings)
   - `nodes` (list, at least one entry)
   - `namespaces` (list, must include `gateway`)
   - `manifests.gateway`, `manifests.bootstrap` (strings, required paths)
3. Validate IPs (`tailscale_ip`, `gateway_tailscale_ip`, each `nodes` entry, optional `gateway_lan_ip`) match IPv4 format.
4. Validate `services.<name>.port` values are integers in range 1-65535.
5. If `lan_network` is present, validate CIDR notation.
6. Check manifest paths reference existing directories under `$KORDINATE_HOME/`.
7. Validate top-level required sections: `network` with `tailnet`.
8. Report valid/invalid with specific issues listed.

## Procedure: `show`

1. Read `$KORDINATE_HOME/profile/config.yaml`.
2. If a cluster name is given, extract and display only that cluster's block.
3. If no argument, display the full config.

## Procedure: `diff`

1. Read current `$KORDINATE_HOME/profile/config.yaml`.
2. Read existing overlays in `$KORDINATE_HOME/profile/overlays/`.
3. Check if overlay values match what config would generate -- look for:
   - IPs in overlays that don't match config
   - Namespaces referenced in overlays but missing from config
   - Services/ports that have drifted
4. Report any drift between config source-of-truth and generated overlays.

## Procedure: `add-cluster`

1. Prompt for required fields: `name`, `description`, `tailscale_ip`, `gateway_tailscale_ip`, `nodes`, `namespaces`.
2. Validate all inputs against schema (IP format, non-empty strings, namespace list includes `gateway`).
3. Prompt for optional fields: `lan_network`, `gateway_lan_ip`, `manifests`, `services`, `workloads`.
4. Add to config.yaml under `clusters.<name>`.
5. Warn: "Run `/config validate` to verify, then `/overlay regenerate <cluster>` to generate overlays."

## Procedure: `update`

1. Parse the dotted path (e.g., `clusters.vandc.tailscale_ip`).
2. Read `$KORDINATE_HOME/profile/config.yaml` and resolve the path to the target field.
3. Show the old value and the proposed new value.
4. Validate the new value against the schema for that field (type, format).
5. Write the update to config.yaml.
6. Warn about downstream effects: "Overlays may need regeneration. Run `/overlay regenerate <cluster>` if this value feeds into overlays."

## Procedure: `schema`

1. Display the contents of the `schema.md` resource file from this skill directory.

## Important Notes

- Alfred never deploys -- it only manages config state.
- After any config write (`add-cluster`, `update`), always warn about overlay/hydration regeneration.
- Use `$KORDINATE_HOME` to reference the kordinate root (resolves to `/kord/kordinate` at runtime).
- The config file path is always `$KORDINATE_HOME/profile/config.yaml`.

## Resources

- [schema.md](schema.md) -- config.yaml schema reference (Level 3)
