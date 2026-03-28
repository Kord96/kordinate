# Health Checks

Level 3 resource for the eval skill (health mode). Defines all structural checks and their severity levels.

## Frontmatter completeness

Every `.md` file under `agents/` and `kords/` must have a `description` field in its YAML frontmatter.

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

## MEMORY.md sync

For each agent's runtime MEMORY.md (`~/.claude/agent-memory/<name>/MEMORY.md`), verify two-way consistency:

- **Broken link** — every entry in MEMORY.md references a target file path. That file must exist on disk.
    - Severity: **ERROR**
- **Missing entry** — every curated memory file (`curated: true`) in the agent's kordinate memory directory should have a corresponding entry in MEMORY.md.
    - Severity: **WARNING**

## MEMORY.md purity

MEMORY.md files must be pure indexes — a list of links to memory files with one-line descriptions. They must not contain:

- Inline memory content (more than one sentence per entry)
- Lifecycle instructions (boot sequences, load-order directives, preload lists)
- Agent identity or behavioral instructions

Severity:
- **WARNING** — MEMORY.md contains lifecycle instructions or inline content

## KORD.json sync

Compare KORD.json entries against actual files on disk:

- **Orphaned entry** — an entry exists in KORD.json but the referenced file does not exist on disk.
    - Severity: **ERROR**
- **Missing entry** — a file exists on disk with a `description` in its frontmatter but has no corresponding entry in KORD.json.
    - Severity: **WARNING**

## Scratchpad staleness

Check the modification date of `memory/scratchpad.md` files for each agent. Use `stat` to read the file's mtime.

- If the scratchpad has not been modified in more than `--stale-days` days (default: 7): **WARNING**

## File size

Check all `.md` files under `agents/`:

- File larger than 20KB: **WARNING**
- File larger than 10KB (but under 20KB): **INFO**

## Kord directory completeness

Every kord directory must conform to the standard template based on its mode:

### Stateful kords (`mode: stateful` in contract.md frontmatter)

Required files:
- `contract.md` — must exist with valid frontmatter
- `data.md` — must exist (may be empty before first consultation)
- `expiry.sh` — must exist and be executable (`-x` permission)
- `review.md` — must exist and contain both `{{DIFF}}` and `{{CACHED_DATA}}` placeholders

Severity:
- **ERROR** — any required file missing
- **ERROR** — `expiry.sh` exists but is not executable
- **ERROR** — `review.md` exists but missing `{{DIFF}}` or `{{CACHED_DATA}}` placeholder

### Stateless kords (`mode: stateless` in contract.md frontmatter)

Required files:
- `contract.md` — must exist with valid frontmatter

Unexpected files (should not exist in stateless kords):
- `data.md`, `expiry.sh`, `review.md`

Severity:
- **WARNING** — unexpected files present in a stateless kord directory

## Duplicate descriptions

Scan all frontmatter `description` fields across all files in the scan targets.

- **Exact match** — two or more files share the exact same description string: **WARNING**
- **Substring relationship** — one file's description is a substring of another's: **INFO**

## Hook validation

Verify that hooks registered in `settings.json` are correctly configured:

- **Hook file exists** — every `command` path referenced in `settings.json` hooks must resolve to an existing file.
    - Severity: **ERROR**
- **Hook is executable** — each referenced hook script must have the executable bit set (`-x`).
    - Severity: **ERROR**
- **Hooks README accuracy** — if a hooks README exists (`hooks/README.md`), each hook listed in it must match a hook registered in `settings.json`, and vice versa.
    - Severity: **WARNING**

## Lifecycle compliance

Verify that kordinate skills and memory files follow lifecycle conventions:

- **Lifecycle wrapper present** — every kord skill directory (`agents/*/kords/*/`) that has a `contract.md` with `mode: stateful` should have its lifecycle managed through `expiry.sh`, not through inline instructions in other files.
    - Severity: **INFO**
- **MEMORY.md is a pure index** — covered by the MEMORY.md purity check above.

## Agent-runtime alignment

Verify that kordinate agent definitions and runtime agent registrations are in sync:

- **Agent directory exists in runtime** — every agent directory under `~/.kord/agents/` must have a corresponding directory under `~/.claude/agents/` (the runtime agent registration).
    - Severity: **ERROR**
- **Agent memory directory exists** — every agent listed in `~/.kord/agents/` must have a corresponding `~/.claude/agent-memory/<name>/` directory.
    - Severity: **WARNING**
- **Agent name consistency** — the `name` field in each agent's `IDENTITY.md` must match the directory name.
    - Severity: **ERROR**

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
