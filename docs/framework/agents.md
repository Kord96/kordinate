# Core Agents

## Root

The orchestrator. Root's `IDENTITY.md` defines the team — all subagents inherit its rules, commands, and hooks. Mapped to the runtime's main agent (e.g. Claude Code's `CLAUDE.md`) via the [linking layer](../reference/linking.md).

**Contains:** agent routing table, [kords](kords.md), team rules.

```
agents/root/
├── IDENTITY.md                    # routing table, triggers, team rules
├── kords/                         # kord definitions
├── memory/
│   ├── static/
│   │   └── team/                  # team rules inherited by all subagents
│   └── dynamic/
│       └── team/                  # team-level dynamic knowledge
└── commands/
```

**Commands** (inherited by all)

| Command | Description |
|---------|-------------|
| `/boot` | Initialize the workstation environment |
| `/consult` | Query an agent without full handoff |
| `/merge` | Merge current session branch |

**Guards** (inherited by all)

| Guard | What it does |
|-------|-------------|
| `guard-git.sh` | Branch model — `main` and `session/*` allowed, `test`/`prod` require auth |
| `guard-md.sh` | `.md` file edits — scribe only |

**Hooks** (inherited by all)

| Hook | What it does |
|------|-------------|
| `auto-merge-to-dev.sh` | After push: creates PR, tries fast-forward main |
| `agent-memory.sh` | Before spawn: regenerates agent's dynamic memory summary |

See [Guards](guards.md) for how exclusive access is enforced.

## Scribe

Documentation gate — present in every team. Only agent authorized to edit `.md` files. All other agents delegate markdown edits to scribe.

Protected by `guard-md.sh` — see [Guards](guards.md).

**Commands**

| Command | Description |
|---------|-------------|
| `/scribe:onboard` | Add a new agent to the team |
| `/scribe:kord` | Define a kord between two agents |
| `/scribe:update-agent-docs` | Update an agent's documentation |
| `/scribe:update-project-docs` | Update project-level docs |
