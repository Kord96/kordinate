# Scribe

Documentation gate — the sole agent authorized to write structured files. All other agents delegate structured edits to scribe.

## Guard Flow

When any agent attempts to write a structured file:

1. Guard hook fires
2. Checks file against registered structured patterns
3. No scribe auth token → blocked, told to delegate to scribe
4. Scribe auth token present → validates against template → allows

Scribe authenticates once per task, performs all writes, removes auth token.

See [Recall System](../framework/memory.md#structured-files) for the full list of structured files and their templates.
