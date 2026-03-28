---
name: keys
description: List, audit, lint, and rotate pass store entries
curated: true
scope: global
---

`/keys <subcommand> [args]`

| Subcommand | Purpose |
|-----------|---------|
| `list` | List all pass entries under `kordinate/` with metadata |
| `audit` | Verify all required keys exist, flag stale/unused entries |
| `lint` | Check naming conventions and structure |
| `show <path>` | Show metadata about a key (exists, type) without revealing the value |
| `add <path>` | Add a new credential to the pass store with validation |
| `rotate <path>` | Rotate a credential -- generate new, deploy, remove old |

## Procedure: `list`

1. Run `pass ls kordinate/` to get the tree of all entries.
2. Load the registry ([registry.md](registry.md)) to get known key metadata.
3. For each entry, display: path, required/optional status, known readers.
4. Flag any entries not in the registry as "unregistered".

### Output Format

```
Pass store: kordinate/ (<date>)

  kordinate/github/token          required  readers: installer, scribe
  kordinate/tailscale/auth_key_workstation  required  readers: workstation entrypoint
  ...
  kordinate/some/unknown_key      UNREGISTERED

Summary: N registered, N unregistered
```

## Procedure: `audit`

1. Load the registry (required keys list from [registry.md](registry.md)).
2. Run `pass ls kordinate/` to get actual entries.
3. Compare: report missing required keys and extra unregistered keys.
4. Cross-reference with `$KORDINATE_HOME/profile/config.yaml` -- if multiple clusters exist, check per-cluster keys exist for each cluster (e.g., `tailscale/auth_key_gateway`, `minio/root_user`, `minio/root_password`).
5. Report summary.

### Output Format

```
Keys audit (<date>)

MISSING REQUIRED:
  x kordinate/<path> -- <description>
    Fix: pass insert kordinate/<path>

PRESENT (ok):
  ok kordinate/<path> -- <description>

UNREGISTERED (not in registry):
  ? kordinate/<path>

PER-CLUSTER CHECK:
  <cluster>: N present, N missing

Summary: N required present, N missing, N unregistered
```

## Procedure: `lint`

1. Run `pass ls kordinate/` to get all entries.
2. Check each entry against naming rules:
   - Must follow `kordinate/<service>/<key>` structure (exactly 3 levels).
   - No spaces, no uppercase letters, no special characters beyond underscore.
   - No deeply nested paths (max 3 levels: `kordinate/service/key`).
3. Warn about any entries that violate convention.

### Output Format

```
Lint: kordinate/ (<date>)

VIOLATIONS:
  ! kordinate/Some/Key -- uppercase not allowed
  ! kordinate/a/b/c/d -- exceeds 3-level depth

CLEAN: N entries
VIOLATIONS: N entries
```

## Procedure: `show`

1. Parse `$ARGUMENTS` for the key path (e.g., `github/token` or `kordinate/github/token`).
2. Normalize to `kordinate/<service>/<key>` form.
3. Check if entry exists: `pass ls kordinate/<service>/<key>`.
4. Look up metadata in the registry: required/optional, description, readers.
5. Display metadata. **Never display the actual value.**

### Output Format

```
Key: kordinate/<service>/<key>
Status: exists | missing
Required: yes | no
Readers: <comma-separated list>
Description: <from registry>
```

## Procedure: `add`

1. Parse `$ARGUMENTS` for the key path.
2. Validate path follows `kordinate/<service>/<key>` naming convention (lint rules).
3. Check if entry already exists -- warn if it does ("key exists, use `rotate` to change it").
4. Run `pass insert kordinate/<path>` (or `pass insert -m kordinate/<path>` for multiline credentials like JSON).
5. If this is a new key type not in the registry, note: "This key is not in the registry. Consider adding it to registry.md."

## Procedure: `rotate`

1. Parse `$ARGUMENTS` for the key path.
2. Verify the key exists in the pass store.
3. Look up readers from the registry.
4. Warn: "After rotation, these systems need redeployment: `<readers list>`"
5. Generate or prompt for the new value.
6. Write new value: `pass insert kordinate/<path>` (overwrites existing).
7. Report what was rotated and what needs redeployment.

### Output Format

```
Rotated: kordinate/<path>
Systems that need redeployment:
  - <reader 1>
  - <reader 2>

Run `/infra roll` or redeploy affected services to pick up the new credential.
```

## Important Notes

- **NEVER echo or display actual credential values** -- only metadata (exists, type, readers).
- Use `pass show` only when writing to a destination (K8s secret, etc.), never for display to the user.
- The pass store is GPG-encrypted under `~/.password-store/`.
- All operations go through the `pass` CLI.
- Use `$KORDINATE_HOME` to reference the kordinate root (resolves to `/kord/kordinate` at runtime).
- Alfred never deploys -- after `rotate`, remind the user to use charon to apply changes.

## Resources

- [registry.md](registry.md) -- canonical pass store schema and key inventory (Level 3)
