# Agents

Four specialized agents, each with a distinct role and exclusive authority over its domain.

| Agent | Role |
|-------|------|
| [charon](charon/) | Infrastructure operations — deployments, cluster management, kubectl |
| [augur](augur/) | Architecture review, pattern authority, and design analysis |
| [sauron](sauron/) | Monitoring, observability, and diagnostics |
| [alfred](alfred/) | Profile/config, credentials, overlays, and environment setup |

## Agent Structure

Each agent directory contains:

```
<agent>/
├── IDENTITY.md    # Role, rules, tools, consultation topics
├── skills/        # Agent-specific skills (SKILL.md each)
└── memory/        # Persistent knowledge (global scope)
```

## How Agents Interact

Agents communicate through delegated tasks and shared filesystem artifacts. The workstation orchestrator routes work to the correct specialist and preserves domain boundaries.

Guards in [hooks/](../hooks/) enforce domain boundaries — charon owns kubectl and deployment operations, sauron owns Grafana/monitoring surfaces, and specialized agents own their scoped files and outputs.
