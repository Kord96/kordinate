---
description: Augur workflow — analyze existing code or design new projects, producing facts and atlas as structured outputs
---
# Workflow

## Skills

| Skill | Purpose |
|-------|---------|
| `/analyze` | Analyze existing codebases — deterministic fact extraction, semantic atlas composition, stories, and narratives |
| `/design` | Design new projects (4 modes: full, api, service, component) |

## Product Roadmap

- [roadmap.md](roadmap.md) — prioritized product plan for telemetry, ask, evolution, feedback, and design

## Structured Outputs

### Facts

Facts are the normalized result of deterministic extraction. They are concrete observations like routes, models, external clients, import edges, jobs, and concepts. Facts are consumed by semantic atlas work and may also be consumed directly for targeted tasks like blast radius or focused summaries.

See `detectors/schema.md` for the canonical facts schema and `schemas/observations/observations-schema.md` for semantic observations.

### Atlas

The atlas is the primary output consumed by all agents (charon, sauron, alfred). It contains:
- Hierarchical components and their connections
- Flows, state, and outside dependencies
- Confirmed concepts and grounded architecture tensions
- Conditionally grounded sections such as actors, events, and domain_model when repo evidence clearly supports them

See `agents/augur/schemas/atlas-schema.md` for the full atlas schema.

## Knowledge Base

- **Concept references** at `references/concepts/` — the matching family-scoped concept file is canonical for concept meaning, explanation, and signatures
- **Framework references** at `references/frameworks/` — `<framework>.md` is canonical for framework explanation and signatures
- **Ontology/index layer** at `memory/indexes/` — abstractions, concept index, anti-pattern index
- **Ontology graph index** at `memory/indexes/ontology-graph.json` and `memory/indexes/ontology-graph.md` — machine-readable and visual graph of concepts, frameworks, abstractions, and cross-links, generated from concept/framework source metadata
- **Detector source assets** at `detectors/` — deterministic fact-production rules and policies
- **Generated bundles** at `.generated/bundles/` — derived prompt/runtime assets, not canonical source
- **Infra-atlas** at `/kord/agents/charon/memory/global/infra-atlas.json` — cluster topology, observability endpoints, workload contract
- **App contract** at `memory/contracts/app-contract.md` — requirements every deployed app must satisfy

## Analyze Workflow

1. Gather source code and identify languages and frameworks
2. Use deterministic detector assets to establish stack context and produce normalized facts
3. Treat `index.json` as the manifest for deterministic run artifacts
4. Use deterministic facts plus planning aids, including `facts/concepts.json`, to guide semantic atlas work
5. Use `agents/augur/schemas/atlas-schema.md`, `agents/augur/schemas/story-schema.md`, and `agents/augur/schemas/narratives-schema.md` as the canonical semantic output contracts

## Design Workflow

1. Read requirements and constraints
2. Select frameworks and patterns from the semantic catalogs
3. Compose architecture with component topology
4. Produce atlas with full detection metadata and infrastructure stubs
