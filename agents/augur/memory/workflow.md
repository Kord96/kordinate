---
description: Augur workflow — analyze existing code or design new projects, producing facts and atlas as structured outputs
---
# Workflow

## Skills

| Skill | Purpose |
|-------|---------|
| `/analyze` | Analyze existing codebases — deterministic fact extraction, semantic atlas composition, stories, and narratives |
| `/design` | Design new projects (4 modes: full, api, service, component) |

## Structured Outputs

### Facts

Facts are the normalized result of deterministic extraction. They are concrete observations like routes, models, external clients, import edges, jobs, and concept-evidence. Facts are consumed by semantic atlas work and may also be consumed directly for targeted tasks like blast radius or focused summaries.

See `schemas/facts-schema.md` for the full schema.

### Atlas

The atlas is the primary output consumed by all agents (charon, sauron, alfred). It contains:
- Hierarchical components and their connections
- Flows, state, and outside dependencies
- Confirmed concepts and grounded architecture tensions
- Optional grounded sections such as actors, events, module graph, security, and API surface

See `agents/augur/schemas/atlas-schema.md` for the full atlas schema.

## Knowledge Base

- **Concept catalog semantics** at `memory/catalog/concepts/` — `<concept>.md` is canonical for concept meaning and architectural implications
- **Framework catalog semantics** at `memory/catalog/frameworks/` — framework primitives, conventions, and common co-occurring concepts
- **Ontology/index layer** at `memory/indexes/` — abstractions, concept index, anti-pattern index
- **Ontology graph index** at `memory/indexes/ontology-graph.json` and `memory/indexes/ontology-graph.md` — machine-readable and visual graph of concepts, frameworks, abstractions, and cross-links, generated from concept/framework source metadata
- **Detector source assets** at `detectors/` — deterministic fact-production rules and policies
- **Generated bundles** at `.generated/bundles/` — derived prompt/runtime assets, not canonical source
- **Infra-atlas** at `/kord/agents/charon/memory/global/infra-atlas.json` — cluster topology, observability endpoints, workload contract
- **App contract** at `memory/contracts/app-contract.md` — requirements every deployed app must satisfy

## Analyze Workflow

1. Gather source code and identify languages and frameworks
2. Use deterministic detector assets to establish stack context and produce normalized facts
3. Treat `facts/index.json` as the manifest for deterministic evidence
4. Use deterministic facts, including `facts/concept-evidence.json`, to guide semantic atlas work
5. Use `agents/augur/schemas/atlas-schema.md`, `agents/augur/schemas/story-schema.md`, and `agents/augur/schemas/narratives-schema.md` as the canonical semantic output contracts

## Design Workflow

1. Read requirements and constraints
2. Select frameworks and patterns from the semantic catalogs
3. Compose architecture with component topology
4. Produce atlas with full detection metadata and infrastructure stubs
