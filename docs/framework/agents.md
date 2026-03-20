# Core Agents

## Base Agent

Every agent inherits these rules and commands.

### Rules

!!! info "Permissions"
    - Only the owning agent can use its exclusive tools (hook-enforced)
    - Never invoke an agent's operational commands directly — spawn the owning agent

!!! note "Conventions"
    - Credentials live in `pass` under `kordinate/`
    - Follow existing patterns — no new libraries, frameworks, or conventions
    - Commit with `[<agent-name>]` in message
    - Project artifacts go in the project repo, not kordinate

!!! tip "Memory"
    Each agent has `static/` (pre-defined structure) + `dynamic/` (free-form) at both global and project scope. See [Memory](memory.md).

### Commands

| Command | Description |
|---------|-------------|
| `/boot` | Initialize the workstation environment |
| `/consult` | Query an agent without full handoff |
| `/merge` | Merge current session branch |
| `/invalidate` | Force re-consultation for an agent |

## Scribe

The only framework-provided agent — present in every team. Manages all `.md` file edits so documentation stays consistent and protected.

Triggered by: `update docs`, `update project docs`, `add api key`, `add mcp`, `update agent docs`, `write readme`

| Command | Description |
|---------|-------------|
| `/scribe:add-mcp` | Add a new MCP server entry |
| `/scribe:update-agent-docs` | Update an agent's documentation |
| `/scribe:update-project-docs` | Update project-level docs |
| `/scribe:update-subagent-memory` | Update agent memory files |
