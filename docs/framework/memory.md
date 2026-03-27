# Recall System

Everything in kordinate — identity, skills, memory, contracts — is knowledge. The recall system defines how knowledge is stored, loaded, and discovered.

## Properties

Every piece of knowledge is described by nine properties:

| Property | Question | Values | Default | Source |
|----------|----------|--------|---------|--------|
| **Path** | Where is it? | file path | required | file location |
| **Name** | Short identifier | text | derived from path | file location |
| **Description** | What is this? | one-line text | required | frontmatter |
| **Template** | Does it follow a template? | `none` / `<template>` | `none` | inferred by type |
| **Curated** | Updated only when explicitly requested? | `true` / `false` | `false` | frontmatter |
| **Preloaded** | Who loads it at startup? | `none` / `all` / `<agent>` | `none` | frontmatter |
| **Owner** | Who owns it? | `team` / `<kord>` / `<agent>` | `agent` | directory path |
| **Scope** | Where does it apply? | `global` / `project` | `global` | directory path |
| **Expiry** | Does it expire? | `none` / `<script>` / `<.md>` | `none` | sibling file |

Only three properties live in frontmatter: **description**, **curated**, and **preloaded**. The rest are derived from the file's location and structure.

- **Preloaded**: `all` = imported into the main session's spawn prompt, survives compaction, everyone sees it. `<agent>` = loaded into that agent's spawn prompt. `none` = loaded on-demand via boot or explicit read.
- **Curated** files are not auto-updated by agents. Changes only happen when a human explicitly requests them. The guard requires scribe auth to write to curated files.
- **Template** files must follow the referenced template.
- **Scope**: `global` lives at `~/.kord/`. `project` lives at `.kord/`. Determined by path, not declared.

For the full list of frontmatter fields per file type (including Claude-native and type-specific fields), see the [Frontmatter Reference](frontmatter.md).

## Registry

`KORD.md` is the human-readable registry of all knowledge. `KORD.json` is the machine-readable version used by the guard and other tools. Both are generated and maintained by [scribe](../agents/scribe.md).

## Enforcement

All writes to kordinate paths (`kord/`) and memory paths go through scribe. A hook on `Write|Edit` blocks unauthorized writes and tells the agent to delegate to scribe. Scribe handles:

- Template validation for templated files
- Scope decision (global vs project) for memory writes
- Writing to both kordinate and runtime-native paths (linking)
- Updating KORD.md and KORD.json with new entries
