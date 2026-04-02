---
name: store
description: Store personal information — credentials, config updates, overlays.
argument-hint: "key <path> <value> | config <yaml-path> <value> | overlay <cluster> <namespace> <content> | platform <env> scaling <agent> <min> <max> <cooldown>"
---

Store personal information managed by alfred. Agents call this via `/kord alfred store` to save credentials, update config, or write overlays.

## Arguments

`$ARGUMENTS` — what to store:

| Command | Action |
|---------|--------|
| `key <path> <value>` | Insert or update a pass store entry |
| `config <yaml-path> <value>` | Update a field in config.yaml |
| `overlay <cluster> <namespace>` | Write or update a namespace overlay (content from stdin or subsequent message) |
| `platform <env> scaling <agent> <min> <max> <cooldown>` | Update KEDA scaling parameters for one agent in the environment's scaling.yaml |

## Procedure

1. **Parse** the first word to determine what's being stored.

2. **Store**:
   - `key` → run `pass insert -f <path>` with the value. Verify with `pass show <path>`.
   - `config` → update the specified YAML path in `$KORDINATE_HOME/profile/config.yaml`. Validate the result with the internal config validation procedure.
   - `overlay` → write to `$KORDINATE_HOME/profile/overlays/<cluster>/<namespace>/`. Create directories if needed. Validate kustomization.yaml if present.
   - `platform` → update the agent's entry in `$KORDINATE_HOME/profile/overlays/platform/<env>/scaling.yaml`. Set minReplicaCount to `<min>`, maxReplicaCount to `<max>`, cooldownPeriod to `<cooldown>`. Create the directory and file if they don't exist.

3. **Validate** — after storing, run the relevant validation:
   - `key` → verify the entry exists in pass
   - `config` → validate the full config.yaml
   - `overlay` → verify kustomization.yaml references valid base paths
   - `platform` → verify scaling.yaml has valid integer values for min/max/cooldown, min <= max, cooldown >= 0

4. **Report** — confirm what was stored and validation result.

## Notes

- Credentials go through the pass store — never written as plaintext files.
- Config updates trigger validation — invalid changes are rejected.
- Overlay writes check for kustomize validity.
- Charon stores overlays here after generating them via `/kord alfred store overlay`.
