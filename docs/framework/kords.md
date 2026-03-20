# Kords

A **kord** is a defined protocol between two agents — what one agent can ask another and what it will get back. Kords are what make agents a team rather than isolated specialists.

```
/scribe:kord deployer designer
```

This establishes what deployer can ask designer (architecture constraints, pattern perspectives) and what designer will provide. Without a kord, agents don't know each other exist.

## Why kords?

Each agent has specialized knowledge in its memory. Deployer knows cluster state. Designer knows architecture patterns. Sauron knows metrics. A kord defines the interface for sharing that knowledge — what questions are valid and what expertise is available.

## Consulting a kord

```
/consult <agent> "<question>"
```

Executes a kord — the consulted agent answers using its memory without taking over the conversation. The caller keeps control. Results are [cached](memory.md#cache) — `/invalidate <agent>` forces a fresh answer.

This differs from **delegation**, where the caller hands off work entirely and the delegated agent takes action (writes files, runs commands, etc.).

## Kord Map

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
