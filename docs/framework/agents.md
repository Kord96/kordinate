# Core Agents

## Root Agent

The orchestrator — receives user messages, matches triggers, spawns the right agent. Root agent's `AGENT.md` defines the team: which agents exist, their triggers, and team-wide rules that all subagents inherit.

Every team has exactly one root agent. The [linking layer](../reference/linking.md) maps it to the runtime's main agent configuration.

Root agent's `AGENT.md` contains:

- **Agent routing table** — triggers → which agent to spawn
- **Consultation directory** — who to consult for what
- **Team rules** — conventions and permissions inherited by all subagents

## Scribe

Present in every team. Manages all `.md` file edits so documentation stays consistent and protected.

Triggered by: `update docs`, `update project docs`, `add api key`, `add mcp`, `update agent docs`, `write readme`

| Command | Description |
|---------|-------------|
| `/scribe:add-mcp` | Add a new MCP server entry |
| `/scribe:update-agent-docs` | Update an agent's documentation |
| `/scribe:update-project-docs` | Update project-level docs |
| `/scribe:update-subagent-memory` | Update agent memory files |

## Every Agent Gets

### Commands

| Command | Description |
|---------|-------------|
| `/boot` | Initialize the workstation environment |
| `/consult` | Query an agent without full handoff |
| `/merge` | Merge current session branch |
| `/invalidate` | Force re-consultation for an agent |

### Hooks

Hooks fire on every tool call — enforcing safety and automating housekeeping.

**Guards**

| Hook | What it guards |
|------|---------------|
| `guard-git.sh` | git push — `main` and `session/*` allowed, `test`/`prod` require auth |
| `guard-md.sh` | All `.md` file edits (scribe only) |

**Automation**

| Hook | When | What it does |
|------|------|-------------|
| `auto-merge-to-dev.sh` | After git push | Creates PR, tries fast-forward main. On failure, signals `/merge`. |
| `agent-memory.sh` | Before agent spawn | Regenerates agent's MEMORY.md if source files changed |

??? abstract "Authentication flow"
    1. Agent copies `profile/locks/<agent>` → `/tmp/.<agent>-auth`
    2. Hook reads both files, allows if they match
    3. Agent removes `/tmp/.<agent>-auth` after completing work

Cache system: hooks use `lib/cache.sh` for hash-based invalidation. See [2D Memory — Cache System](memory.md#cache-system).
