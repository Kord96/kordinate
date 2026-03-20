# Architecture Overview

```mermaid
flowchart TB
    ROOT[Root Agent]

    subgraph team[Team]
        A1[Agent A] <-.->|consult| A2[Agent B]
        A2 <-.->|consult| A3[Agent C]
        A1 <-.->|consult| A3
    end

    ROOT -.->|consult| A1
    ROOT -.->|consult| A2
    ROOT -.->|consult| A3
```

The root agent is the user's existing agent (Claude, Codex, Cursor). The [linking layer](../reference/linking.md) enhances it with kordinate's coordination capabilities:

- **[Memory](memory.md)** — structured knowledge (static/dynamic × global/project) with caching and refresh
- **[Hooks](#role-enforcement)** — enforce that only the right agent performs protected operations
- **Routing** — trigger words automatically spawn the right specialist
- **[Consultation](#consultation)** — agents query each other for expertise they lack

## Agent Structure

Every agent follows the same layout. `KORD.md` defines identity, `memory/` holds knowledge.

### KORD.md

| Section | What it contains |
|---------|-----------------|
| **Description** | One-line role definition |
| **Commands** | Slash commands the agent owns |
| **Rules** | Behavioral constraints |
| **Consultation** | What it answers when consulted |
| **Cache Sources** | What files define this agent's knowledge freshness |

### Directory skeleton

```
agents/<agent>/
├── KORD.md                        # identity + cache sources
├── memory/
│   ├── static/
│   │   ├── instructions/          # procedures (consultation, workflow, auth)
│   │   └── ...                    # domain knowledge
│   └── dynamic/                   # auto-managed (operational notes, caches)
└── commands/                      # slash command definitions
```

## Guarded Hooks

A guarded hook is a hook that only lets a specific agent through. The mechanism:

1. Root defines the trigger — when the guarded hook fires (e.g., on every `.md` edit)
2. Every agent has a secret key. Before performing a guarded action, the authorized agent writes its key to a temp location
3. The guard script compares the key against what it expects — passes if they match, blocks otherwise

### Framework guarded hooks

**Documentation guard** — `.md` file edits must go through scribe.

Root registers a hook on Edit/Write of `.md` files. If any agent other than scribe attempts the edit, the hook blocks it and the fail message asks to delegate to scribe.

**Cache refresh guard** — only the cache owner can refresh its cache.

When an agent's knowledge changes, only that agent's refresh hook decides whether to invalidate. Other agents cannot trigger a refresh on behalf of someone else.

Teams can define additional guarded hooks for their agents (e.g., kubectl writes → deployer only, Grafana → sauron only).

## Consultation

```
/consult <agent> "<question>"
```

An agent answers using its memory without taking over the conversation. Results are [cached](memory.md#cache) — `/invalidate <agent>` forces a fresh answer.

### Consultation Matrix

Owned by [root](root.md) — defines who consults whom and for what. Lives in root's `KORD.md`.

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
