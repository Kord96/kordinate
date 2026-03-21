# Overview

```mermaid
flowchart TB
    ROOT[Root Agent]

    subgraph team[Team]
        A1[Agent A] <-.->|consult| A2[Agent B]
        A1 <-.->|consult| A3[Agent C]
        A2 <-.->|consult| A3
        A1 <-->|delegate| A2
        A1 -->|delegate| SC[Scribe]
        A2 -->|delegate| SC
        A3 -->|delegate| SC
    end

    ROOT -.->|consult| A1
    ROOT -.->|consult| A2
    ROOT -.->|consult| A3
    ROOT -->|delegate| SC
```

**[Root](agents.md#root)** is the user's existing agent (Claude, Codex, Cursor).

**[Scribe](agents.md#scribe)** ships with the framework — it guards all `.md` edits and handles onboarding new agents. Always part of the team.

Kordinate adds:

- **[Recall System](memory.md)** — structured knowledge (static/dynamic × global/project) with caching and refresh
- **[Guards](guards.md)** — hook-based enforcement that only the right agent performs protected operations
- **[Kords](kords.md)** — defined protocols between agents for sharing expertise

## Agent Structure

Every agent follows the same layout: `IDENTITY.md` defines identity, `memory/` holds knowledge, `commands/` holds slash commands. Use `/scribe:onboard` to add new agents to the team.
