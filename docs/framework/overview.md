# Overview

```mermaid
flowchart TB
    ROOT[Root Agent]

    subgraph team[Team]
        A1[Agent A] <-.->|consult| A2[Agent B]
        A1 -.->|consult| A3["Agent C\n(beorn)"]
        A3 -.->|consult| A1
        A2 <-.->|consult| A3
        A1 -->|consult| SC[Scribe]
        A2 -->|consult| SC
    end

    ROOT -.->|consult| A1
    ROOT -.->|consult| A2
    ROOT -->|consult| SC
```

## What Kordinate Adds

- **[Recall System](memory.md)** — structured knowledge (static/dynamic × global/project) with caching and refresh
- **[Guards](guards.md)** — hook-based enforcement that only the right agent performs protected operations
- **[Kords](kords.md)** — defined protocols between agents for sharing expertise
- **[Nesting Agents](beorn.md)** — subagents can consult other subagents at any depth

**[Root](#root)** is the user's existing agent — Claude Code, Codex, Cursor, or any compatible runtime. Root orchestrates a team of subagents, each with its own identity, memory, and commands. **[Scribe](#scribe)** guards all `.md` edits and handles onboarding. Both are always present.

Subagents communicate through **[kords](kords.md)** — protocols that define what one agent provides to another. A pair of agents can have multiple kords for different topics (shown as separate arrows above). When a subagent needs to consult another, a **beorn** — a short-lived clone that assumes the target agent's identity — is spawned to handle the request and return the result. The [beorn MCP server](beorn.md) manages this lifecycle.

## Agent Structure

Every agent follows the same layout. Use `/scribe:onboard` to add new agents to the team.

```
agents/<name>/
├── IDENTITY.md              # role, triggers, commands, rules
├── memory/
│   ├── static/              # curated domain knowledge
│   └── dynamic/             # auto-managed (consultations, operational notes)
└── commands/                # slash command definitions
```

## Core Agents

### Root

The orchestrator. Root's `IDENTITY.md` defines the team — all subagents inherit its rules, commands, and hooks. Mapped to the runtime's main agent (e.g. Claude Code's `CLAUDE.md`) via the [linking layer](../dev/linking.md).

All inherited by subagents:

**Commands** — `/boot` (catch up on context), `/consult` (query or delegate to an agent), `/merge` (merge session branch).

**Guards** — `guard-git.sh` (branch protection), `guard-md.sh` (scribe-only `.md` edits). See [Guards](guards.md).

**Hooks** — `auto-merge-to-dev.sh` (post-push PR + fast-forward), `agent-memory.sh` (pre-spawn memory refresh).

### Scribe

Documentation gate. Only agent authorized to edit `.md` files — all other agents delegate markdown edits to scribe.

Protected by `guard-md.sh` — see [Guards](guards.md).

**Commands** — `/scribe:onboard` (add agent), `/scribe:kord` (define kord), `/scribe:update-agent-docs`, `/scribe:update-project-docs`.

### Beorn

A beorn is a short-lived agent clone — it assumes another agent's identity (IDENTITY.md + memory), handles a single consultation, and exits. The [beorn MCP server](beorn.md) is the factory that spawns these clones on demand.

**Tools** — `mcp__beorn__delegate` (spawn a beorn as any agent), `mcp__beorn__status` (server health).

`/consult` uses the beorn server as its transport layer. See [Beorn](beorn.md) for architecture details.
