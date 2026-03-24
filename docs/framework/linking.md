# Linking

Kordinate is runtime-agnostic. Agent files live at `~/.kord/` in a portable format. The **linking layer** converts them to whatever the runtime expects — it's the only part that changes when switching runtimes.

## Kordinate

```
~/.kord/
├── MAP.md                          # router — auto-generated from frontmatter
├── team/
│   ├── memory/*.md                 # shared conventions, standards
│   └── kords/
│       └── <kord>/
│           ├── contract.md         # consultation protocol
│           └── data.md             # cached results with expiry
├── <agent>/                            # general, scribe, deployer, etc.
│   ├── identity.md                 # role, tools, workflow, rules
│   ├── skills/<name>/SKILL.md      # per-agent skills
│   └── memory/*.md                 # domain knowledge, notes
├── settings.json                   # permissions, hooks, env vars
└── .mcp.json                       # MCP server configuration
```

Every agent has the same structure. `general` is the default main session agent.

## Claude Code

Claude Code reads from `~/.claude/` (user scope) and `.claude/` (project scope). The linker targets user scope.

### Direct Copy

No transformation needed.

| Source | Target |
|--------|--------|
| `settings.json` | `~/.claude/settings.json` |
| `.mcp.json` | `~/.claude/.mcp.json` |
| `<agent>/skills/` | `~/.claude/skills/<agent>/` |

### Main Agent

The general agent becomes the main Claude Code session.

| Source | Target | Operation |
|--------|--------|-----------|
| `general/identity.md` body + `MAP.md` | `~/.claude/CLAUDE.md` | merge |
| `general/memory/` | `~/.claude/projects/<project>/memory/` | copy (`MAP.md` → `MEMORY.md`) |

### Subagents

Other agents are linked as native Claude Code subagents. [Beorn](../agents/beorn.md) enables P2P between them.

| Source | Target | Operation |
|--------|--------|-----------|
| `<agent>/identity.md` | `~/.claude/agents/<name>.md` | copy (frontmatter already compatible) |
| `<agent>/memory/MAP.md` | `~/.claude/agent-memory/<name>/MEMORY.md` | rename |

Subagent memory is a single `MEMORY.md` in Claude (200-line preload). Multi-file memory and kords stay in `~/.kord/` — Beorn reads them directly at runtime.

### What Beorn Handles

These don't map to Claude's filesystem. Beorn serves them at runtime:

- Agent multi-file memory beyond `MEMORY.md`
- Kords (consultation protocols and cached data)
- Memory properties (expiry, structured enforcement)
- P2P invocation between subagents

### Differences

| | Kordinate | Claude Code |
|---|---|---|
| **Hierarchy** | No hierarchy — any agent can be root or subagent | Fixed — one main session, subagents below it |
| **Identity** | Every agent has `<agent>/identity.md`, same format | Main session uses `CLAUDE.md`; subagents use `agents/<name>.md` |
| **Shared context** | `MAP.md` — universal router | `CLAUDE.md` — inherited from main to all subagents |
| **Memory** | Agent-owned folders, per-file properties via frontmatter | Main: auto memory with topic files. Subagents: single `MEMORY.md` |
| **Expiry** | Files declare staleness via scripts or markdown | No expiry — memory grows indefinitely |
| **Structure enforcement** | `structured` property + guards | No enforcement |
| **Skills** | Per-agent: `<agent>/skills/` | Global: `skills/<name>/SKILL.md` |
