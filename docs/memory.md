# Memory System

How agents store and discover knowledge.

## Per-Agent Structure

```
agents/<agent>/
├── AGENT.md              # role, commands, rules
├── instructions/         # procedures (workflow, auth, tools)
├── memory/
│   ├── static/           # curated knowledge (generic)
│   └── dynamic/          # auto-managed notes (site-specific, encrypted)
└── commands/             # slash command definitions
```

## Three Layers

| Layer | Location | What goes here | Encrypted |
|-------|----------|---------------|-----------|
| **Static** | `agents/<agent>/memory/static/` | Curated knowledge that applies to any installation — architecture, libraries, troubleshooting | no |
| **Dynamic** | `agents/<agent>/memory/dynamic/` | Auto-managed notes accumulated during use — cluster IPs, debug findings, operational tips | yes |
| **Project** | `<repo>/.claude/agent-memory/<agent>/` | Knowledge tied to a specific project — metrics catalogs, health checks | no |

## How Agents Get Context on Startup

The `agent-memory.sh` hook fires before every agent spawn. It:

1. Computes a hash of the agent's `instructions/` + `memory/static/` + `shared/MEMORY.md`
2. If the hash changed (or `MEMORY.md` is missing): regenerates `memory/dynamic/MEMORY.md`
3. If unchanged: skips (fast path)

The generated `MEMORY.md` contains:
- **Shared rules** from `shared/MEMORY.md`
- **Instructions** from `instructions/*.md` (always inlined)
- **Static knowledge** — inlined if small (<500 lines), indexed if large
- **Notes** — preserved from previous `MEMORY.md` (Claude's auto-managed section)

Claude auto-loads `MEMORY.md` on startup. The agent gets full context without needing to read files itself.

## Shared Memory

```
agents/shared/
└── MEMORY.md             # common rules for all agents
```

Injected into every agent's generated `MEMORY.md` by the hook. Contains operational rules all agents share (credentials, commit conventions, tool restrictions).

## Project Conventions

Agents also discover knowledge from project repos:

| Convention | Agent | Purpose |
|-----------|-------|---------|
| `<repo>/manifests/` | deployer | k8s manifests |
| `<repo>/monitoring/` | sauron | Dashboards, health checks |
| `<repo>/.claude/agent-memory/<agent>/` | any | Project-specific agent notes |
