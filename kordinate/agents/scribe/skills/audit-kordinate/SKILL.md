---
name: audit-kordinate
description: Read-only health check for the memory and kordinate system — scans files and reports issues.
curated: true
---

Read-only health check for the memory and kordinate system. Scans all agents' memory files, frontmatter, registry entries, and reports issues. Never modifies files.

$ARGUMENTS: `[--scope global|project|all] [--agent <name>] [--stale-days 7]`

## Procedure

1. **Parse arguments** — defaults: `scope=all`, `stale-days=7`, no agent filter (scan all agents).

2. **Determine scan targets** based on `--scope`:
    - `global` — scan `$KORDINATE_HOME` (`~/.kord/`)
    - `project` — scan `.kord/` in the current project root
    - `all` — scan both
    - If `--agent <name>` is provided, restrict to that agent's directories only.

3. **Run checks** — execute every check defined in [checks.md](checks.md) against the scan targets.

4. **Group findings** — organize results by severity (`ERROR` first, then `WARNING`, then `INFO`), then by agent within each severity level.

5. **Output structured report** — print findings as a table with summary counts. See [checks.md](checks.md) for the output format.

6. **Report** — print findings. Never modify any files.

## Rules

- Pure read-only — never create, edit, or delete any file.
- `ERROR` = broken invariant that will cause runtime failures.
- `WARNING` = likely problem that should be fixed.
- `INFO` = potential improvement, informational only.
