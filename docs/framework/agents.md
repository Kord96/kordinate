# Core Agents

## Root

The orchestrator. Routes user messages to the right agent. Root's `KORD.md` defines the team — all subagents inherit its rules, commands, and hooks.

Mapped to the runtime's main agent by the [linking layer](../reference/linking.md) (e.g. Claude Code's `CLAUDE.md`).

**Contains:** agent routing table, consultation directory, team rules.

```
agents/root/
├── KORD.md                    # routing table, triggers, team rules
├── memory/
│   ├── static/
│   │   └── team/              # team rules inherited by all subagents
│   └── dynamic/
│       └── team/              # consultation cache
└── commands/
```

**Commands** (inherited by all)

| Command | Description |
|---------|-------------|
| `/boot` | Initialize the workstation environment |
| `/consult` | Query an agent without full handoff |
| `/merge` | Merge current session branch |
| `/invalidate` | Force re-consultation for an agent |

**Hooks** (inherited by all)

| Hook | What it does |
|------|-------------|
| `guard-git.sh` | Branch model — `main` and `session/*` allowed, `test`/`prod` require auth |
| `guard-md.sh` | `.md` file edits — scribe only |
| `auto-merge-to-dev.sh` | After push: creates PR, tries fast-forward main |
| `agent-memory.sh` | Before spawn: regenerates MEMORY.md if sources changed |

??? abstract "Hook-based role enforcement"
    Protected operations (kubectl, Grafana, `.md` edits) are restricted to specific agents via guard hooks. Each guard uses a lock-file handshake to verify the calling agent is authorized:

    1. Agent copies `profile/locks/<agent>` → `/tmp/.<agent>-auth`
    2. Hook reads both files, allows if they match
    3. Agent removes `/tmp/.<agent>-auth` after completing work

    This ensures only the owning agent can perform its exclusive operations — even if another agent attempts to, the hook blocks it.

## Scribe

Documentation gate — present in every team. Only agent authorized to edit `.md` files. All other agents delegate markdown edits to scribe.

Enforced by `guard-md.sh`: the hook blocks Edit/Write on `.md` files unless scribe's auth token is present.

**Triggers:** `update docs`, `update project docs`, `add api key`, `add mcp`, `update agent docs`, `write readme`

**Commands**

| Command | Description |
|---------|-------------|
| `/scribe:add-mcp` | Add a new MCP server entry |
| `/scribe:update-agent-docs` | Update an agent's documentation |
| `/scribe:update-project-docs` | Update project-level docs |
| `/scribe:update-subagent-memory` | Update agent memory files |
