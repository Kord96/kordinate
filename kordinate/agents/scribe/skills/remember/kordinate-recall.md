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
| Global | `~/.claude/kord/agents/<name>/memory/*.md` |
| Project | `.claude/kord/agents/<name>/memory/*.md` |

## KORD.md

The registry at `~/.claude/kord/KORD.md` (global) or `.claude/kord/KORD.md` (project) must be updated when adding new files. Each entry has: path, description, and any non-default properties.
