# Recall System

Everything in kordinate — identity, skills, memory, contracts — is knowledge. The recall system defines how knowledge is stored, loaded, and discovered.

## Properties

Every piece of knowledge is described by eight properties:

| Property | Question | Values | Default |
|----------|----------|--------|---------|
| **Path** | Where is it? | file path | required |
| **Name** | Short identifier | text | derived from path |
| **Description** | What is this? | one-line text | required |
| **Template** | Does it follow a template? | `none` / `<template>` | `none` |
| **Curated** | Updated only when explicitly requested? | `true` / `false` | `false` |
| **Preloaded** | Loaded at startup? | `true` / `false` | `false` |
| **Owner** | Who owns it? | `team` / `<kord>` / `<agent>` | `agent` |
| **Scope** | Where does it apply? | `global` / `project` | `global` |
| **Expiry** | Does it expire? | `none` / `<script>` / `<.md>` | `none` |

- **Curated** files are not auto-updated by agents. Changes only happen when a human explicitly requests them.
- **Template** files must follow the referenced template.
- **Scope**: `global` knowledge is user-wide. `project` knowledge is project-specific.

## Registry

`KORD.md` is the registry of all knowledge. Generated and maintained by scribe.
