---
name: store
description: Store personal information — credentials, config updates, overlays.
argument-hint: "key <path> <value> | config <yaml-path> <value> | overlay <cluster> <namespace> <content> | platform <env> scaling <agent> <min> <max> <cooldown>"
---

Store personal information managed by alfred. Agents call this via `/kord alfred store` to save credentials, update config, or write overlays.
When a caller asks Alfred to store or update something in Alfred's domain, Alfred should perform the write directly and report the result. Do not answer with a suggested command unless the caller explicitly asks for command syntax.

## Arguments

`$ARGUMENTS` — what to store:

| Command | Action |
|---------|--------|
| `key <path> <value>` | Insert or update a pass store entry |
| `config <yaml-path> <value>` | Update a field in config.yaml |
| `profile <name> <yaml-or-json>` | Create or update one entry in `agents/alfred/profile/model-profiles.yaml` |
| `overlay <cluster> <namespace>` | Write or update a namespace overlay (content from stdin or subsequent message) |
| `platform <env> scaling <agent> <min> <max> <cooldown>` | Update KEDA scaling parameters for one agent in the environment's scaling.yaml |

## Procedure

1. **Parse** the first word to determine what's being stored.

2. **Store**:
   - `key` → run `pass insert -f <path>` with the value. Verify with `pass show <path>`.
   - `config` → update the specified YAML path in `$KORDINATE_HOME/agents/alfred/profile/config.yaml`. Validate the result with the internal config validation procedure, then refresh the runtime projection.
   - `profile` → update the named entry in `$KORDINATE_HOME/agents/alfred/profile/model-profiles.yaml`. Validate that required fields are present (`profile`, `model`, optional `base_url`, credential refs), then refresh the runtime projection.
   - `overlay` → write to `$KORDINATE_HOME/agents/alfred/profile/overlays/<cluster>/<namespace>/`. Create directories if needed. Validate kustomization.yaml if present, then refresh the runtime projection.
   - `platform` → update the agent's entry in `$KORDINATE_HOME/agents/alfred/profile/overlays/platform/<env>/scaling.yaml`. Set minReplicaCount to `<min>`, maxReplicaCount to `<max>`, cooldownPeriod to `<cooldown>`. Create the directory and file if they don't exist, then refresh the runtime projection.

3. **Validate** — after storing, run the relevant validation:
   - `key` → verify the entry exists in pass
   - `config` → validate the full config.yaml
   - `overlay` → verify kustomization.yaml references valid base paths
   - `platform` → verify scaling.yaml has valid integer values for min/max/cooldown, min <= max, cooldown >= 0

4. **Publish projection** — run `$KORDINATE_HOME/shared/scripts/publish-profile.sh` after any successful config/profile/overlay write so `shared/runtime/profile/` stays in sync.

5. **Report** — confirm what was stored and validation result.
   If the caller asked for the change to be performed, perform it. Do not stop at describing the `store` command shape.

### Response style

Use terse bullets only:
- `stored:` <paths or refs>
- `validated:` <yes/no plus brief reason>
- `follow-up:` <only if action is required>

Do not narrate your steps.
Do not include prose summaries if bullets are enough.
Never echo secret values.
If nothing changed, return one bullet: `no change`.
Do not return command templates unless the caller explicitly asks for them.

## Notes

- Credentials go through the pass store — never written as plaintext files.
- Config updates trigger validation — invalid changes are rejected.
- Overlay writes check for kustomize validity.
- Charon stores overlays here after generating them via `/kord alfred store overlay`.
