# Kordinate Recall System

Level 3 resource for the remember skill.

## Properties

Every piece of knowledge has these properties (tracked in KORD.md):

| Property | Values | Default |
|----------|--------|---------|
| Path | file path | required |
| Name | text | derived from path |
| Description | one-line text | required |
| Template | `none` / `<template>` | `none` |
| Curated | `true` / `false` | `false` |
| Preloaded | `none` / `all` / `<agent>` | `none` |
| Owner | `team` / `<kord>` / `<agent>` | `agent` |
| Scope | `global` / `project` | `global` |
| Expiry | `none` / `<script>` / `<.md>` | `none` |

## Kordinate Paths

Memory files live inside `kord/` in the runtime's directory structure:

| Scope | Path |
|-------|------|
| Global | `$KORDINATE_HOME/agents/<name>/memory/*.md` |
| Project | `.kord/agents/<name>/memory/*.md` |

## KORD.md

Two registries — one per scope:

- `$KORDINATE_HOME/KORD.md` — global registry
- `.kord/KORD.md` — project registry

Update when adding new files. Each entry is one line: path + description. Only list non-default properties.

Example:

```markdown
## Agents

- `agents/deployer/identity.md` — Infrastructure operations, sole kubectl authority (curated, preloaded: deployer, template: identity)
- `agents/deployer/memory/cluster-topology.md` — Current cluster layout and service endpoints

## Routes

- `agents/deployer/routes.yaml` — Route definitions for deployer agent (cluster-health, deploy-service)
- `agents/scribe/routes.yaml` — Route definitions for scribe agent (write-memory, register-agent)

## Team

- `team/memory/coding-standards.md` — Team-wide coding standards (curated)
```
