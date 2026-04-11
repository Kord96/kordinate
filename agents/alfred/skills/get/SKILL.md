---
name: get
description: Retrieve personal information — config, credentials, overlays. Verifies caller identity.
argument-hint: "config [cluster] | key <path> | overlay <cluster> [namespace] | platform <env> [scaling] | status"
---

Retrieve personal information managed by alfred.
When a caller asks Alfred for one of these resources, Alfred should execute the retrieval itself and return the requested result. Do not answer with a suggested command unless the caller explicitly asks for command syntax.

## Arguments

`$ARGUMENTS` — what to retrieve:

| Command | Returns |
|---------|---------|
| `config` | Full config.yaml content |
| `config <cluster>` | Config for a specific cluster |
| `key <path>` | Credential value from pass store (e.g., `key kordinate/grafana_admin/password`) |
| `overlay <cluster>` | Overlay directory listing for a cluster |
| `overlay <cluster> <namespace>` | Specific namespace overlay content |
| `platform <env>` | All platform overlay contents (kustomization.yaml, scaling.yaml, resources.yaml) for an environment |
| `platform <env> scaling` | Just the KEDA scaling config (scaling.yaml) for an environment |
| `profile <name>` | A reusable backend profile definition from `agents/alfred/profile/model-profiles.yaml` |
| `status` | Summary: config validity, credential count, overlay readiness |

## Procedure

1. **Parse** the first word to determine what's being requested.

2. **Retrieve**:
   - `config` → read `$KORDINATE_HOME/agents/alfred/profile/config.yaml`. If cluster specified, extract that cluster's section.
   - `key` → run `pass show <path>`. Never log or echo the value outside the response.
   - `overlay` → read from `$KORDINATE_HOME/agents/alfred/profile/overlays/<cluster>/`. List contents or read specific namespace.
   - `platform` → read from `$KORDINATE_HOME/agents/alfred/profile/overlays/platform/<env>/`. Return all files, or just scaling.yaml if `scaling` subcommand given.
   - `profile` → read the named entry from `$KORDINATE_HOME/agents/alfred/profile/model-profiles.yaml`.
   - `status` → run config validation, count pass entries, check overlay directories exist.

Simple-task rules:
- `key <path>` means `pass show <path>`.
- If the target source-of-truth file is already clear from the request, read it directly.
- Do not search first unless the direct action fails.

3. **Return** the requested information. For `key`, return the value directly — the caller is responsible for handling it securely.
   If the caller asked for a specific value or file content, return that result directly instead of describing the `get` invocation.

Runtime/bootstrap consumers should prefer the published projection under `$KORDINATE_HOME/shared/runtime/profile/` when they do not need Alfred's authoritative source tree.

### Response style

Default to terse bullets.
If the request is not for a secret value, avoid narration and return only the requested data plus minimal labels.
If the request is for `status`, use short bullets only.
Do not include process commentary.
Do not return example command shapes unless the caller explicitly asks for them.

## Notes

- This is read-only. To modify config/keys/overlays, use `/kord alfred store`.
- Credentials are never cached — each request reads from the pass store.
- Config validation uses the same checks as the internal `config validate` procedure.
