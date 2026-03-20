# Architecture Overview

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

**[Root](root.md)** is the user's existing agent (Claude, Codex, Cursor). The [linking layer](../reference/linking.md) enhances it with kordinate's coordination capabilities.

**[Scribe](scribe.md)** ships with the framework — it guards all `.md` edits and handles [onboarding new agents](scribe.md#onboarding-an-agent). Always part of the team.

Kordinate adds:

- **[Memory](memory.md)** — structured knowledge (static/dynamic × global/project) with caching and refresh
- **[Hooks](#guarded-hooks)** — enforce that only the right agent performs protected operations
- **[Kords](#kords)** — defined protocols between agents for sharing expertise

## Agent Structure

Every agent follows the same layout: `KORD.md` defines identity, `memory/` holds knowledge, `commands/` holds slash commands. See [Onboarding an Agent](scribe.md#onboarding-an-agent) for the full structure and how new agents are created.

## Guarded Hooks

A guarded hook only lets a specific agent through.

```mermaid
flowchart LR
    A[Any agent] -->|action| G{Root Guard}
    G -->|key matches| OK[allowed]
    G -->|no key| BLOCK[blocked — delegate<br/>to key holder]
```

1. Root defines the trigger — when the guard fires
2. The authorized agent writes its secret key before acting
3. The guard checks the key — passes or blocks

### Core guarded hooks

**Documentation guard** — `.md` edits must go through scribe. Any other agent is blocked and told to delegate.

**Cache refresh guard** — only the cache owner can refresh its own cache.

Teams can add their own (e.g., kubectl writes → deployer agent, Grafana MCP calls → sauron agent).

## Kords

A **kord** is a defined protocol between two agents — what one agent can ask another and what it will get back. Kords are what make agents a team rather than isolated specialists.

```
/scribe:kord deployer designer
```

This establishes what deployer can ask designer (architecture constraints, pattern perspectives) and what designer will provide. Without a kord, agents don't know each other exist.

### Why kords?

Each agent has specialized knowledge in its memory. Deployer knows cluster state. Designer knows architecture patterns. Sauron knows metrics. A kord defines the interface for sharing that knowledge — what questions are valid and what expertise is available.

### Consulting a kord

```
/consult <agent> "<question>"
```

Executes a kord — the consulted agent answers using its memory without taking over the conversation. The caller keeps control. Results are [cached](memory.md#cache) — `/invalidate <agent>` forces a fresh answer.

This differs from **delegation**, where the caller hands off work entirely and the delegated agent takes action (writes files, runs commands, etc.).

### Kord Map

Owned by [root](root.md) — defines all kords in the team. Lives in root's `KORD.md`.

??? abstract "Example: infra team"

    === "Deployer asks"

        | Consultant | Provides |
        |-----------|----------|
        | designer | Pattern deployment perspective, architecture constraints |
        | sauron | Monitoring impact of infra changes, metric dependencies |

    === "Sauron asks"

        | Consultant | Provides |
        |-----------|----------|
        | designer | Pattern monitoring perspective — what to observe |
        | deployer | Live cluster state, pod health, resource usage |

    === "Designer asks"

        | Consultant | Provides |
        |-----------|----------|
        | deployer | Infrastructure reality — live cluster state, resource usage |
        | sauron | Observability gaps — what is and isn't being monitored |

    === "Scribe asks"

        | Consultant | Provides |
        |-----------|----------|
        | designer | Architecture context — component topology, design patterns |
        | sauron | Monitoring context — metrics, dashboards, health checks |
        | deployer | Infrastructure context — cluster state, deployment details |
