# Kordinate

```mermaid
flowchart TB
    ROOT[Root Agent] <-.->|consult| A1[Agent A]
    ROOT <-.->|consult| A2[Agent B]
    ROOT <-.->|consult| A3[Agent C]
    A1 <-.->|consult| A2
    A2 <-.->|consult| A3
    A1 <-.->|consult| A3
```

A framework for kording specialized agents into a team. Each agent owns a domain with exclusive tools, shares a [consultation protocol](framework/consultation.md) and [2D memory](framework/memory.md) with the team, and is kept in its lane by [hooks](framework/agents.md#root). Run `/scribe:kord` to add your own.

## Explore

<div class="grid cards" markdown>

-   **[Framework](framework/agents.md)**

    The agent protocol -- roles, commands, memory model, hooks, and consultation.

-   **[Example: Infra Team](infra/infrastructure.md)**

    Deployer, sauron, and designer managing multi-cluster k8s infrastructure.

-   **[Kord your own](guides/how-to-kord.md)**

    Add a new agent with `/scribe:kord` — or see how designer was built.

-   **[Resources](reference/index.md)**

    Design patterns, shared libraries, and source mapping.

</div>
