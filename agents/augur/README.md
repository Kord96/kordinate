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
- [memory/tools.md](memory/tools.md) — Tool reference
- [memory/indexes/](memory/indexes/) — Ontology and index layer
- [memory/contracts/](memory/contracts/) — Normative contracts
- [memory/catalog/concepts/](memory/catalog/concepts/) — Concept semantics catalog
- [memory/catalog/frameworks/](memory/catalog/frameworks/) — Framework semantics catalog

### Detector source
- [detectors/concepts/](detectors/concepts/) — Deterministic concept detector assets
- [detectors/frameworks/](detectors/frameworks/) — Deterministic framework detector assets

### Generated bundles
- [bundles/memory/](bundles/memory/) — Model-facing semantic memory bundles for analyze holistic/selective modes
- [bundles/runtime/](bundles/runtime/) — Final runtime analyze bundles with distinct cacheable prefixes for holistic and selective execution
- [bundles/detectors/](bundles/detectors/) — Generated detector execution bundles

### Facts-first synthesis
- [schemas/facts-schema.md](schemas/facts-schema.md) — normalized extraction contract
- [scripts/synthesize_atlas_from_facts.py](scripts/synthesize_atlas_from_facts.py) — deterministic CLI that turns `facts/` into atlas scaffolding

## Rules

- Framework-first: if a framework primitive exists, use it
- Facts-first: normalize evidence before concept inference and atlas synthesis
- Convention over configuration: follow established patterns
- Proportional effort: don't rewrite working code for marginal improvement
- Concrete: always include specific file paths and what should change
- Validate with Gemini MCP for complex architectural decisions
