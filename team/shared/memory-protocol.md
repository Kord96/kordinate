---
description: How agents persist knowledge through the memory system
---

# Memory Protocol

You have two types of memory, stored under your agent directory:

- **Global** (`memory/global/`) — loaded at boot via CLAUDE.md. Reusable knowledge across projects.
- **Project** (`memory/projects/<project>/`) — loaded per-job by the pod daemon. Findings about a specific codebase.

## Reading memory

Global memory is pre-loaded into your context. Project memory paths are provided with each job — read the files at that path for prior context.

## Writing memory

Post insights to the memory endpoint. The curator deduplicates and merges them into the appropriate directory.

```bash
curl -s http://localhost:9090/memory-update \
  -H "Content-Type: application/json" \
  -d '{
    "path": "<topic>.md",
    "content": "<insight>",
    "scope": "global|project",
    "project": "<project-name>"
  }'
```

- `path` — filename grouping related insights (e.g., `patterns.md`, `debt.md`)
- `scope` — `global` for reusable knowledge, `project` for codebase-specific findings
- `project` — the project name (required when scope is `project`)

Do not write directly to `memory/` paths — those are managed by the curator.

## What to remember

- Patterns or anti-patterns you identified
- Facts about infrastructure, services, or configurations you discovered
- Decisions that were made and why
- Workarounds for issues you encountered

## What not to remember

- Ephemeral task details (what you were asked to do this time)
- Information already in git (code changes, commit history)
- Things derivable from running a command
