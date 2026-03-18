# Memory System

How agents store and discover knowledge in kordinate.

## Per-Agent Structure

```
agents/<agent>/
├── AGENT.md              # identity: role, commands, rules
├── instructions/         # procedures: how to do things
│   ├── workflow.md       # step-by-step process
│   ├── auth.md           # authentication procedure
│   ├── tools.md          # available tools
│   └── consultation.md   # how to answer when consulted
├── memory/
│   ├── static/           # curated knowledge (generic, any install)
│   │   ├── *.md          # architecture, troubleshooting, etc.
│   │   └── libraries/    # library reference docs
│   └── dynamic/          # auto-managed notes (site-specific, encrypted)
│       └── *.md          # accumulated during use
└── commands/             # slash command definitions
    └── *.md
```

## What Goes Where

| Content | Location | Tracked | Encrypted |
|---------|----------|---------|-----------|
| Agent identity (role, commands, rules) | `AGENT.md` | yes | no |
| Procedures (workflow, auth, tools) | `instructions/` | yes | no |
| Generic knowledge (any install) | `memory/static/` | yes | no |
| Site-specific notes (IPs, debug history) | `memory/dynamic/` | yes | **yes** |
| Project-specific notes | `<repo>/.claude/agent-memory/<agent>/` | per-project | no |
| Slash command definitions | `commands/` | yes | no |

## How Agents Discover Knowledge

On startup (defined in `shared/AGENT.md`):

1. **Read `memory/`** — all files in static/ and dynamic/
2. **Check project repo** — `<repo>/.claude/agent-memory/<agent>/` if in a project
3. **Check project conventions** — `<repo>/manifests/` (deployer), `<repo>/monitoring/` (sauron)
4. **Run `/boot`**

Instructions are read on demand when the agent needs to perform a specific action.

## Shared Knowledge

```
agents/shared/
├── AGENT.md              # rules all agents follow
├── MEMORY.md             # this file
├── libraries/            # shared library docs (future)
└── patterns/             # shared pattern docs (future)
```

Currently, libraries and patterns live in individual agent memory (e.g., `designer/memory/static/patterns/`). These may move to `shared/` in the future if multiple agents need the same knowledge.

## Linking to Claude Code

The installer maps kordinate's memory to Claude Code's conventions:

| Kordinate path | Claude Code path | Method |
|----------------|------------------|--------|
| `agents/<agent>/memory/dynamic/` | `~/.claude/agent-memory/<agent>/` | symlink |
| `agents/<agent>/AGENT.md` | `~/.claude/agents/<agent>/CLAUDE.md` | copy (renamed) |
| `agents/shared/AGENT.md` | `~/.claude/CLAUDE.md` | copy (renamed) |

Claude auto-loads `MEMORY.md` from `agent-memory/<agent>/` (which points to `memory/dynamic/`). The linking layer can generate this file or merge content from multiple sources as needed.

## Project-Level Memory

Projects can have per-agent knowledge at `<repo>/.claude/agent-memory/<agent>/`:

```
your-project/
├── .claude/
│   └── agent-memory/
│       ├── sauron/       # metrics catalogs, health check docs
│       └── deployer/     # deploy-specific notes
├── manifests/            # k8s manifests (deployer convention)
└── monitoring/           # dashboards, health checks (sauron convention)
```

This is separate from kordinate — it lives in the project repo and is project-scoped.
