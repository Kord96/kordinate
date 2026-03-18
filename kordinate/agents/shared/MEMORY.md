# Shared Memory

Common rules for all agents.

## Rules

- Credentials live in `pass` under `kordinate/`. Agent auth locks live in `profile/locks/`.
- Follow the project's existing patterns — don't introduce new libraries, frameworks, or conventions
- All `.md` files are protected — only the scribe agent may edit them
- Commit with `[<your-name>]` in the message
- Project-specific artifacts go in the project repo, not kordinate
- Only the deployer may run kubectl write operations
- Only the sauron may use Grafana MCP tools
- Only the deployer may use Redis MCP tools

## Memory

| What to write | Where |
|---------------|-------|
| Generic knowledge | `memory/static/` |
| Site-specific notes | `memory/dynamic/` |
| Project-specific | `<repo>/.claude/agent-memory/<you>/` |
