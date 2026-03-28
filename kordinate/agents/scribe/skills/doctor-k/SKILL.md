---
name: doctor-k
description: Health-check the kordinate system — structural checks, runtime validation, and end-to-end tests. Use when checking system health, verifying after changes, or debugging integration issues.
argument-hint: "[--scope global|project|all] [--e2e] [--agent <name>] [--stale-days N]"
curated: true
scope: global
---

Comprehensive health check for the kordinate runtime. Scans agents, skills, hooks, memory, settings, and kord contracts for structural problems, broken links, and configuration drift. Never modifies files.

## Procedure

1. **Parse arguments** — defaults: `scope=all`, `stale-days=7`, no agent filter (scan all agents).

2. **Determine scan targets** based on `--scope`:
    - `global` — scan `$KORDINATE_HOME` (`~/.kord/`)
    - `project` — scan `.kord/` in the current project root
    - `all` — scan both
    - If `--agent <name>` is provided, restrict to that agent's directories only.

3. **Run structural checks** — execute checks in [health-checks.md](health-checks.md) (runtime-agnostic).

4. **Run runtime checks** — execute checks in [runtime-claude.md](runtime-claude.md) (Claude Code specific: MEMORY.md sync, agent alignment, hooks, CLAUDE.md, skills).

5. **Run e2e checks** (if `--e2e` flag) — execute checks in [e2e-checks.md](e2e-checks.md). These actually invoke the system (spawn agents, route kords, write memories). Slower, has side effects. Skip if structural/runtime checks have ERRORs.

6. **Group findings** — organize results by severity (`ERROR` first, then `WARNING`, then `INFO`), then by check category (structural, runtime, e2e).

7. **Report** — print findings. Structural and runtime checks never modify files. E2e checks clean up after themselves.

## Rules

- Pure read-only — never create, edit, or delete any file.
- `ERROR` = broken invariant that will cause runtime failures.
- `WARNING` = likely problem that should be fixed.
- `INFO` = potential improvement, informational only.

## Reference Files

- [health-checks.md](health-checks.md) — Structural health checks (runtime-agnostic: frontmatter, kords, manifest, tree sync)
- [runtime-claude.md](runtime-claude.md) — Claude Code runtime checks (MEMORY.md, agent alignment, hooks, CLAUDE.md, skills)
- [e2e-checks.md](e2e-checks.md) — End-to-end checks (spawn agents, lifecycle compliance, kord routing, memory persistence, guard enforcement)
