---
name: install-k
description: Convenience alias for register runtime — installs or reinstalls kordinate.
argument-hint: "[--local] [--restore <repo-url>]"
curated: true
scope: global
---

Thin wrapper around `register runtime`. Use `/install` for quick access; use `/register runtime` directly for full options.

## Mapping

| install form | delegates to |
|---|---|
| `/install` | `register runtime` (interactive, asks for source) |
| `/install --local` | `register runtime --dev .` (detect local repo as source) |
| `/install --restore <url>` | `register runtime --from <url>` |

## Procedure

Parse flags and delegate to the register skill's runtime mode. This skill only translates arguments.
