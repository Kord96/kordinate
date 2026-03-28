# Agents

Four specialized agents, each with a distinct role and exclusive authority over its domain.

| Agent | Role | Kords provided |
|-------|------|---------------|
| [deployer](deployer/) | Infrastructure operations — deployments, cluster management, kubectl | `deployer-default` |
| [designer](designer/) | Architecture review and pattern authority | `designer-default`, `pattern-review` |
| [sauron](sauron/) | Monitoring, observability, and code validation | `sauron-default`, `monitoring-impact` |
| [scribe](scribe/) | Documentation gate and runtime linker | `scribe-default`, `create-kord`, `onboard`, `remember`, `sanitize` |

## Agent Structure

Each agent directory contains:

```
<agent>/
├── IDENTITY.md    # Role, rules, tools, consultation topics
├── skills/        # Agent-specific skills (SKILL.md each)
└── memory/        # Persistent knowledge (global scope)
```

## How Agents Interact

Agents communicate through **kords** — contracts that define a provider, requester, mode, and response format. Any agent can consult another by invoking `/kord <question>`, which routes to the appropriate provider based on the contract.

Guards in [hooks/](../hooks/) enforce domain boundaries — deployer owns kubectl, sauron owns Grafana, scribe owns markdown and memory paths.
