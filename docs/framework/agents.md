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

All inherited by subagents:

**Commands** — `/boot` (init workstation), `/consult` (query agent), `/merge` (merge session branch).

**Guards** — `guard-git.sh` (branch protection), `guard-md.sh` (scribe-only `.md` edits). See [Guards](guards.md).

**Hooks** — `auto-merge-to-dev.sh` (post-push PR + fast-forward), `agent-memory.sh` (pre-spawn memory refresh).

## Scribe

Documentation gate — present in every team. Only agent authorized to edit `.md` files. All other agents delegate markdown edits to scribe.

Protected by `guard-md.sh` — see [Guards](guards.md).

**Commands** — `/scribe:onboard` (add agent), `/scribe:kord` (define kord), `/scribe:update-agent-docs`, `/scribe:update-project-docs`.
