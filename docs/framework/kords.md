# Kords

A **kord** is a consultation protocol between two agents — a contract that defines what one agent can ask another and what it will get back. Each kord connects a **consulter** (the agent asking) to a **consultant** (the agent answering).

Without kords, agents are isolated specialists. Kords are what make them a team.

## Format

Every kord follows the same structure:

| Field | Description |
|-------|-------------|
| **Consulter** | The agent asking |
| **Consultant** | The agent answering |
| **Provides** | What the consultant offers — specific items with expected format |
| **Additional Notes** | Open-ended guidance for queries outside the structured list |

??? abstract "Example: deployer → designer"

    | Field | Value |
    |-------|-------|
    | **Consulter** | deployer |
    | **Consultant** | designer |

    **Provides:**

    - Pattern deployment perspective — checklist of pattern compliance
    - Architecture constraints — list of violations or concerns
    - Data flow impact — affected components and connections

    **Additional Notes:**

    Any architecture question related to a deployment change. Designer answers from its pattern library and project architecture knowledge.

## Defining a kord

```
/scribe:kord deployer designer
```

Scribe walks through the format interactively — who provides what, in what format, and any additional notes. The resulting kord is stored in root's `KORD.md`.

## Using a kord

```
/consult <agent> "<question>"
```

Consults an agent — the consultant answers using its memory without taking over the conversation. The consulter keeps control. Results are [cached](memory.md#cache) — `/invalidate <agent>` forces a fresh answer.

This differs from **delegation**, where the consulter hands off work entirely and the delegated agent takes action (writes files, runs commands, etc.).

## Kord Map

The full set of kords in a team. Owned by [root](root.md), lives in root's `KORD.md`.

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
