# Augur

Architecture review and pattern authority — reviews design consistency, identifies patterns, and produces architectural analysis.

## Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| [analyze](skills/analyze/SKILL.md) | `/analyze <project>` | Scan a project for recognized architectural patterns and produce atlas/story outputs |
| [design](skills/design/SKILL.md) | `/design <mode>` | Design new systems or components using Augur's pattern vocabulary |

## Memory and detectors

### Source memory
- [memory/MEMORY.md](memory/MEMORY.md) — Memory entrypoint
- [memory/workflow.md](memory/workflow.md) — Review workflow
- [memory/roadmap.md](memory/roadmap.md) — Product roadmap and phase ordering
- [memory/tools.md](memory/tools.md) — Tool reference
- [memory/concepts/](memory/concepts/) — Canonical concept and framework references
- [memory/indexes/](memory/indexes/) — Ontology and index layer
- [memory/contracts/](memory/contracts/) — Normative contracts

### Detector source
- [detectors/concepts/](detectors/concepts/) — Deterministic concept detector assets
- [detectors/frameworks/](detectors/frameworks/) — Deterministic framework detector assets

### Generated bundles
- [.generated/bundles/memory/](.generated/bundles/memory/) — Model-facing semantic memory bundles for analyze holistic/selective modes
- [.generated/bundles/runtime/](.generated/bundles/runtime/) — Final runtime analyze bundles with distinct cacheable prefixes for holistic and selective execution
- [.generated/bundles/detectors/](.generated/bundles/detectors/) — Generated detector execution bundles

### Facts-first synthesis
- [detectors/schema.md](detectors/schema.md) — canonical normalized facts contract
- [schemas/facts/facts-schema.md](schemas/facts/facts-schema.md) — consumer-facing facts contract entrypoint
- [schemas/observations/observations-schema.md](schemas/observations/observations-schema.md) — semantic observations contract
- [scripts/synthesize_atlas_from_facts.py](scripts/synthesize_atlas_from_facts.py) — deterministic CLI that turns `facts/` into atlas scaffolding
- [detectors/utils/](detectors/utils/) — detector-owned deterministic fact generation and synthesis helpers

## Rules

- Framework-first: if a framework primitive exists, use it
- Facts-first: normalize evidence before concept inference and atlas synthesis
- Convention over configuration: follow established patterns
- Proportional effort: don't rewrite working code for marginal improvement
- Concrete: always include specific file paths and what should change
- Validate with Gemini MCP for complex architectural decisions
