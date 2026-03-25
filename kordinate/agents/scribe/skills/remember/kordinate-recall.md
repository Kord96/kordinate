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
| Preloaded | `true` / `false` | `false` |
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

- `agents/deployer/identity.md` — Infrastructure operations, sole kubectl authority (curated, preloaded, template: identity)
- `agents/deployer/memory/cluster-topology.md` — Current cluster layout and service endpoints

## Kords

- `kord/deployer-default/contract.md` — General cluster questions (curated, template: contract)
- `kord/deployer-default/data.md` — Cached cluster state (template: data, expiry: expiry.sh)

## Team

- `team/memory/coding-standards.md` — Team-wide coding standards (curated)
```
