# Designer

Architecture review and pattern authority — reviews design consistency and identifies patterns.

## Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| [detect-concepts](skills/detect-concepts/SKILL.md) | `/designer:detect-concepts <project>` | Scan a project for recognized architectural patterns |

## Kords Provided

| Kord | Mode | Requesters | Description |
|------|------|-----------|-------------|
| [designer-default](../../kords/designer-default/contract.md) | stateful | any | General architecture and design questions — topology, patterns, data flow, failure modes |
| [pattern-review](../../kords/pattern-review/contract.md) | stateful | deployer, sauron | Architecture review for deployment and monitoring changes — violations by severity |

## Memory

| File | Description |
|------|-------------|
| [app-contract.md](memory/app-contract.md) | App contract |
| [concepts.md](memory/concepts.md) | Index of recognized architectural concepts by category |
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
