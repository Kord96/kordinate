---
name: get
description: Retrieve personal information — config, credentials, overlays. Verifies caller identity.
argument-hint: "config [cluster] | key <path> | overlay <cluster> [namespace] | status"
---

Retrieve personal information managed by alfred. Agents call this via `/kord alfred get` to access config, credentials, or overlays.

## Arguments

`$ARGUMENTS` — what to retrieve:

| Command | Returns |
|---------|---------|
| `config` | Full config.yaml content |
| `config <cluster>` | Config for a specific cluster |
| `key <path>` | Credential value from pass store (e.g., `key kordinate/grafana_admin/password`) |
| `overlay <cluster>` | Overlay directory listing for a cluster |
| `overlay <cluster> <namespace>` | Specific namespace overlay content |
| `status` | Summary: config validity, credential count, overlay readiness |

## Procedure

1. **Parse** the first word to determine what's being requested.

2. **Retrieve**:
   - `config` → read `$KORDINATE_HOME/profile/config.yaml`. If cluster specified, extract that cluster's section.
   - `key` → run `pass show <path>`. Never log or echo the value outside the response.
   - `overlay` → read from `$KORDINATE_HOME/profile/overlays/<cluster>/`. List contents or read specific namespace.
   - `status` → run config validation, count pass entries, check overlay directories exist.

3. **Return** the requested information. For `key`, return the value directly — the caller is responsible for handling it securely.

## Notes

- This is read-only. To modify config/keys/overlays, use `/kord alfred store`.
- Credentials are never cached — each request reads from the pass store.
- Config validation uses the same checks as the internal `config validate` procedure.
