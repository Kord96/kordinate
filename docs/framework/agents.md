# Core Agents

## Root

The orchestrator — receives user messages, matches triggers, spawns the right agent. Root's `AGENT.md` defines the team and everything subagents inherit.

Every team has exactly one root. The [linking layer](../reference/linking.md) maps root to the runtime's main agent (e.g. Claude Code's `CLAUDE.md`, Codex's config, Cursor's rules).

### Identity

- **Agent routing table** — triggers → which agent to spawn
- **Consultation directory** — who to consult for what
- **Team rules** — conventions and permissions

### Commands (inherited by all)

| Command | Description |
|---------|-------------|
| `/boot` | Initialize the workstation environment |
| `/consult` | Query an agent without full handoff |
| `/merge` | Merge current session branch |
| `/invalidate` | Force re-consultation for an agent |

### Hooks (inherited by all)

Hooks fire on every tool call — enforcing safety and automating housekeeping.

| Hook | What it does |
|------|-------------|
| `guard-git.sh` | git push — `main` and `session/*` allowed, `test`/`prod` require auth |
| `guard-md.sh` | All `.md` file edits (scribe only) |
| `auto-merge-to-dev.sh` | After git push: creates PR, tries fast-forward main |
| `agent-memory.sh` | Before agent spawn: regenerates MEMORY.md if sources changed |

??? abstract "Authentication flow"
    1. Agent copies `profile/locks/<agent>` → `/tmp/.<agent>-auth`
    2. Hook reads both files, allows if they match
    3. Agent removes `/tmp/.<agent>-auth` after completing work

## Scribe

Present in every team. Manages all `.md` file edits so documentation stays consistent and protected.

Triggered by: `update docs`, `update project docs`, `add api key`, `add mcp`, `update agent docs`, `write readme`

| Command | Description |
|---------|-------------|
| `/scribe:add-mcp` | Add a new MCP server entry |
| `/scribe:update-agent-docs` | Update an agent's documentation |
| `/scribe:update-project-docs` | Update project-level docs |
| `/scribe:update-subagent-memory` | Update agent memory files |
