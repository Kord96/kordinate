# Health Checks

Level 3 resource for the doctor-k skill. Structural checks that verify kordinate's internal consistency. Runtime-agnostic — no assumptions about which runtime (Claude Code, etc.) is in use.

## Frontmatter completeness

Every `.md` file under `agents/` must have a `description` field in its YAML frontmatter.

Additional required fields by file type:
- **IDENTITY.md** — must also have `curated`, `scope`, `preloaded`
- **Memory files** (`agents/*/memory/*.md`) — must have `description` and `curated`

Severity:
- **ERROR** — `description` missing on IDENTITY.md or contract files
- **WARNING** — `description` or `curated` missing on memory files

## Frontmatter validity

Validate that frontmatter field values are within their allowed ranges:
- `scope` must be `global` or `project`
- `preloaded` must be `all`, `none`, or a valid agent name (check against `agents/` subdirectories)
- `curated` must be `true` or `false`

Severity: **ERROR** for any invalid value.

## KORD.json sync

Compare KORD.json entries against actual files on disk:

- **Orphaned entry** — an entry exists in KORD.json but the referenced file does not exist on disk (check both memory files and route entries).
    - Severity: **ERROR**
- **Missing entry** — a file exists on disk with a `description` in its frontmatter but has no corresponding entry in KORD.json. Routes defined in `routes.yaml` files should also appear.
    - Severity: **WARNING**

## Scratchpad staleness

Check the modification date of `memory/scratchpad.md` files for each agent. Use `stat` to read the file's mtime.

- If the scratchpad has not been modified in more than `--stale-days` days (default: 7): **WARNING**

## File size

Check all `.md` files under `agents/`:

- File larger than 20KB: **WARNING**
- File larger than 10KB (but under 20KB): **INFO**

## Route registry validation

Every agent that has skills should have a `routes.yaml` defining its routes.

### Route file presence

For each agent directory that contains a `skills/` subdirectory, check for `routes.yaml`:
- **ERROR** — agent has skills but no `routes.yaml`

### Route name uniqueness

Collect all route `name` fields across all `routes.yaml` files:
- **ERROR** — two or more routes share the same name (even across different agents)

### Cache input paths

For each route with a `cache` section, validate that `inputs` paths resolve to existing files or directories:
- **WARNING** — a cache input path does not exist on disk

### Skill references

For each route, verify the `skill` field references a skill directory that exists under the agent's `skills/` or under global `skills/`:
- **ERROR** — route references a skill that does not exist

## Duplicate descriptions

Scan all frontmatter `description` fields across all files in the scan targets.

- **Exact match** — two or more files share the exact same description string: **WARNING**
- **Substring relationship** — one file's description is a substring of another's: **INFO**

## Manifest integrity

If `$KORDINATE_HOME/.manifest.json` exists:
- All files listed in the manifest must exist on disk: **ERROR** if missing
- Curated package files should have hashes matching the manifest: **WARNING** if drifted

If the manifest does not exist: **INFO** (migration may be needed).

## Dev/installable tree sync

If running from a dev repo (`.dev-source` exists), compare the dev tree (`agents/`) against the installable tree (`kordinate/agents/`):
- Skills that exist in one tree but not the other: **WARNING**
- Routes defined in one tree but not the other: **WARNING**
- IDENTITY.md content that differs between trees: **INFO**

## Output format

Present findings as a table, grouped by severity then agent:

```
| Severity | Agent | Check | File | Detail |
|----------|-------|-------|------|--------|
```

Follow the table with a summary line:

```
Summary: X errors, Y warnings, Z info
```
