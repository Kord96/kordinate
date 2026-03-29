# Health Checks

Level 3 resource for the doctor-k skill. Structural checks that verify kordinate's internal consistency. Updated for the KORD.json central manifest system.

Also used by `/install` as the post-install verification step.

## KORD.json integrity

KORD.json is the central manifest. Verify:

- KORD.json exists at `$KORDINATE_HOME/KORD.json`: **ERROR** if missing
- KORD.json is valid JSON: **ERROR** if parse fails
- KORD-seed.json exists (factory reset baseline): **WARNING** if missing
- No duplicate skill names across agents: **ERROR** if duplicates
- No overlapping guard patterns: **WARNING** if two guards match the same command
- All dir patterns match at least one file on disk: **WARNING** if orphaned

## KORD.json file sync

Compare KORD.json file entries against actual files on disk:

- **Orphaned entry** — KORD.json has an entry but the file doesn't exist: **ERROR**
- **Missing entry** — file exists in `agents/*/memory/` with content but no KORD.json entry: **WARNING**
- Every `preload` value must be `all`, `none`, or a valid agent name: **ERROR** if invalid
- Every `owner` must be a valid agent name, `team`, or `main`: **ERROR** if invalid
- Every `validation` must be an agent name or a script path that exists: **ERROR** if invalid

## Agent memory separation

Each agent should have its own memory isolated from other agents:

- Agent memory files are in `agents/<name>/memory/`: **ERROR** if files in wrong agent's dir
- Agent memory KORD.json entries have `owner` matching the agent name: **ERROR** if mismatch
- Agents with `preload` entries should have at least one preloaded file: **WARNING** if none

## Boot preload

Verify boot can load preloaded files:

- `team/scripts/preload.py` exists and is executable: **ERROR** if missing
- For each agent, run preload.py and verify it produces output: **WARNING** if empty
- Shared protocols (`preload: all`) exist and are non-empty: **ERROR** if missing

## Project memory

Verify project-scoped memory works:

- If `.kord/` exists in the current project root, it should have an `agents/` directory: **WARNING** if malformed
- Project memory files should not duplicate global memory files exactly: **INFO** if duplicates found

## Framework file protection

Verify KORD.json dir entries protect framework files:

- All IDENTITY.md files are covered by a `dir` entry with `validation: scribe`: **ERROR** if unprotected
- All SKILL.md files are under a protected dir pattern: **ERROR** if unprotected
- All hooks are under a protected dir pattern: **ERROR** if unprotected
- `settings.json` has a file entry with validation: **ERROR** if unprotected
- KORD.json and KORD-seed.json have guard entries: **ERROR** if unprotected

## Warden validation

Verify the validation token system:

- Warden validate skill exists: **ERROR** if missing
- Registered validator scripts exist on disk: **ERROR** if missing

## Subagent communication

Verify agents can call other agents:

- Kord MCP server is configured in `~/.claude.json`: **ERROR** if missing
- Agent-gate hook exists and is executable: **ERROR** if missing
- Agent lock files exist for each agent in `profile/locks/`: **WARNING** if missing

## Install hygiene

Verify no stale files from previous installs:

- No `skills/` directory at `$KORDINATE_HOME` root (old global skills): **ERROR** if exists
- No `KORD.md` at `$KORDINATE_HOME` root (deprecated): **WARNING** if exists
- No `routes.yaml` in agent directories (replaced by KORD.json): **INFO** if exists
- No stale agent skills in `~/.claude/skills/` (only team skills belong there): **ERROR** if agent skills found
- No stale agent definitions in `~/.claude/agents/` for agents not in `$KORDINATE_HOME/agents/`: **ERROR**

## Sanitize push guard

Verify secrets scanning works:

- `sanitize-scan.py` exists in warden's sanitize skill: **ERROR** if missing
- `patterns.yaml` exists and has patterns: **ERROR** if missing or empty
- Git push guard entry exists in KORD.json: **WARNING** if missing

## Content audit (with `--deep`)

These checks read file content, not just metadata. Slower but catches semantic staleness. Skip unless `--deep` is passed.

### Framework file staleness

For files in KORD-seed.json (the framework skeleton):
- Scan for references to deleted agents (deployer, designer): **WARNING**
- Scan for references to deleted skills (/detect-concepts, /architect, /infra, /assess-debt, /map-dependencies, /review-api, /train-detection): **WARNING**
- Scan for references to removed tools (write_memory, Beorn): **WARNING**
- Scan for stale frontmatter fields (curated, scope, preloaded still present): **WARNING**
- Scan for references to KORD.md or generate-kord.sh: **WARNING**
- Scan for references to routes.yaml: **WARNING**

### Template compliance

Check files against their expected structure:
- **IDENTITY.md** — must have: Skills table, Capabilities section, Rules section, Consultation section: **WARNING** if missing sections
- **SKILL.md** — must have: name and description in frontmatter, Arguments or procedure section: **WARNING** if missing
- **Concept files** (`concepts/*/concept.md`) — must have: Recognition > Signatures section: **INFO** if missing

### Preload audit

Review preload configuration:
- Preloaded files not modified in 30+ days: **INFO** — still relevant?
- Preloaded files larger than 10KB: **WARNING** — expensive context, consider trimming
- Total preload size per agent (sum of all preloaded files): **WARNING** if > 50KB
- Memory files frequently written to but not preloaded: **INFO** — consider preloading

### Cross-reference validity

Check that text content references valid system state:
- Agent names mentioned in file content should exist in `$KORDINATE_HOME/agents/`: **WARNING** if referencing nonexistent agent
- Skill names mentioned (e.g., `/analyze`, `/monitor`) should exist in KORD.json skill entries: **WARNING** if stale
- File paths mentioned should resolve: **WARNING** if path doesn't exist
- KORD.json descriptions should roughly match file content: **INFO** if description seems outdated

### Description accuracy

For each KORD.json file entry, compare description against file's first heading or first paragraph:
- Description says something significantly different from content: **INFO**

## Scratchpad staleness

Check modification date of `memory/scratchpad.md` for each agent:

- Not modified in `--stale-days` days (default: 7): **WARNING**

## File size

Check all `.md` files under `agents/`:

- Larger than 20KB: **WARNING**
- Larger than 10KB: **INFO**

## Duplicate descriptions

Scan KORD.json `description` fields:

- Two or more entries share the exact same description: **WARNING**

## Manifest integrity

If `$KORDINATE_HOME/.manifest.json` exists:
- All listed files must exist on disk: **ERROR** if missing
- Empty manifest: **WARNING**

If manifest does not exist: **INFO**

## Output format

Present findings as a table, grouped by severity then agent:

```
| Severity | Agent | Check | File | Detail |
|----------|-------|-------|------|--------|
```

Summary line:
```
Summary: X errors, Y warnings, Z info
```
