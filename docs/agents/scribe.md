# Scribe

Documentation gate — the sole agent authorized to write structured files. All other agents delegate structured edits to scribe.

## What Scribe Owns

- **Structured files** — identity, commands, kords, manifests. Scribe validates writes against templates.
- **Scribe registry** — the pattern list that defines what's structured. The guard reads this.
- **Index files** — auto-generated per agent and team. Lists on-demand files.

## How It Works

When any agent attempts to write a structured file:

1. Guard hook fires
2. Checks file against registered structured patterns
3. No scribe auth token → blocked, told to delegate to scribe
4. Scribe auth token present → validates against template → allows

Scribe authenticates once per task, performs all writes, removes auth token.
