# Root

The orchestrator. Root's `IDENTITY.md` defines the team — all subagents inherit its rules, commands, and hooks.

Mapped to the runtime's main agent (e.g. Claude Code's `CLAUDE.md`) via the [linking layer](../reference/linking.md).

**Contains:** agent routing table, [kords](kords.md), team rules.

```
agents/root/
├── IDENTITY.md                    # routing table, triggers, team rules
├── memory/
│   ├── static/
│   │   └── team/              # team rules inherited by all subagents
│   └── dynamic/
│       └── team/              # team-level dynamic knowledge
└── commands/
```

**Commands** (inherited by all)

| Command | Description |
|---------|-------------|
| `/boot` | Initialize the workstation environment |
| `/consult` | Query an agent without full handoff |
| `/merge` | Merge current session branch |

**Hooks** (inherited by all)

| Hook | What it does |
|------|-------------|
| `guard-git.sh` | Branch model — `main` and `session/*` allowed, `test`/`prod` require auth |
| `guard-md.sh` | `.md` file edits — scribe only |
| `auto-merge-to-dev.sh` | After push: creates PR, tries fast-forward main |
| `agent-memory.sh` | Before spawn: regenerates agent's dynamic memory summary |

See [Guards](guards.md) for how exclusive access is enforced.
