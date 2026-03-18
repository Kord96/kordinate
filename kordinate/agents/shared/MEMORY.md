# Shared Memory

Common knowledge for all agents.

## On Startup

1. Read all files in your `memory/` directory
2. If in a project repo: check for `<repo>/.claude/agent-memory/<you>/`, `<repo>/manifests/`, `<repo>/monitoring/`
3. Run `/boot`

## Rules

- Credentials live in `pass` under `kordinate/`. Agent auth locks live in `profile/locks/`.
- Follow the project's existing patterns — don't introduce new libraries, frameworks, or conventions
- All `.md` files are protected — only the scribe agent may edit them
- Commit with `[<your-name>]` in the message
- Project-specific artifacts go in the project repo, not kordinate
- Only the deployer agent may run kubectl write operations
- Only the sauron agent may use Grafana MCP tools
- Only the deployer agent may use Redis MCP tools

## Memory

| What to write | Where |
|---------------|-------|
| Generic knowledge | `memory/static/` |
| Site-specific notes | `memory/dynamic/` |
| Project-specific | `<repo>/.claude/agent-memory/<you>/` |
