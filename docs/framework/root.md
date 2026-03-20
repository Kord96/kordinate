# Root

The orchestrator. Routes user messages to the right agent. Root's `KORD.md` defines the team — all subagents inherit its rules, commands, and hooks.

Mapped to the runtime's main agent by the [linking layer](../reference/linking.md) (e.g. Claude Code's `CLAUDE.md`).

**Contains:** agent routing table, [consultation matrix](consultation.md#consultation-matrix), team rules.

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

See [Architecture Overview — Role Enforcement](consultation.md#role-enforcement) for how hooks enforce exclusive access.
