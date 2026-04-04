# Augur

Architecture review and pattern authority — reviews design consistency, identifies patterns, and produces architectural analysis.

## Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| [detect-patterns](skills/detect-patterns/SKILL.md) | `/designer:detect-patterns <project>` | Scan a project for recognized architectural patterns |

## Legacy Kord Contracts

These entries describe older compatibility contracts and are no longer the preferred orchestration path. Use explicit delegation to `augur` instead.

| Kord | Mode | Requesters | Description |
|------|------|-----------|-------------|
| [designer-default](../../kords/designer-default/contract.md) | stateful | any | Legacy architecture/design questions contract |
| [pattern-review](../../kords/pattern-review/contract.md) | stateful | deployer, sauron | Legacy deployment/monitoring review contract |

## Memory

| File | Description |
|------|-------------|
| [app-contract.md](memory/app-contract.md) | App contract |
| [patterns.md](memory/patterns.md) | Index of recognized architectural patterns by category |
| [patterns/](memory/patterns/) | 16 pattern references (circuit-breaker, saga, CQRS, DDD, hexagonal, etc.) |
| [libraries.md](memory/libraries.md) | Index of shared libraries that implement patterns |
| [libraries/](memory/libraries/) | Library references (klog, nokrashi-tools, orchestrator, stoik) |
| [tools.md](memory/tools.md) | Tools reference — Gemini MCP for architecture validation |
| [workflow.md](memory/workflow.md) | Review workflow — identify, compare, review, report |

## Rules

- Framework-first: if a framework primitive exists, use it
- Convention over configuration: follow established patterns
- Proportional effort: don't rewrite working code for marginal improvement
- Concrete: always include specific file paths and what should change
- Validate with Gemini MCP for complex architectural decisions
