---
description: Augur workflow — analyze existing code or design new projects, producing facts and atlas as structured outputs
---
# Workflow

## Skills

| Skill | Purpose |
|-------|---------|
| `/analyze` | Analyze existing codebases — pattern detection, debt assessment, failure modes |
| `/design` | Design new projects (4 modes: full, api, service, component) |

## Structured Outputs

### Facts

Facts are the normalized result of deterministic extraction. They are concrete observations like routes, models, external clients, import edges, jobs, and concept-evidence. Facts are consumed by semantic atlas work and may also be consumed directly for targeted tasks like blast radius or focused summaries.

See `schemas/facts-schema.md` for the full schema.

### Atlas

The atlas is the primary output consumed by all agents (charon, sauron, alfred). It contains:
- Components and their connections
- Failure modes with structured detection metadata (signals, concerns, source patterns)
- Infrastructure requirements (vitals config, dashboard stubs, resource defaults)
- Dependency map

See `schemas/atlas-schema.md` for the full schema.

## Knowledge Base

- **Concept catalog semantics** at `memory/catalog/concepts/` — `concept.md` remains canonical for concept meaning and architectural implications
- **Framework catalog semantics** at `memory/catalog/frameworks/` — framework primitives, conventions, and common co-occurring concepts
- **Ontology/index layer** at `memory/indexes/` — abstractions, concept index, anti-pattern index
- **Detector source assets** at `detectors/` — deterministic framework and concept detection rules and policies
- **Generated bundles** at `bundles/` — compiled memory bundles for model preload and bundled detector execution assets
- **Infra-atlas** at `/kord/agents/charon/memory/global/infra-atlas.json` — cluster topology, observability endpoints, workload contract
- **App contract** at `memory/contracts/app-contract.md` — requirements every deployed app must satisfy

## Analyze Workflow

1. Gather source code and identify languages and frameworks
2. Use framework detector assets to establish stack context and prioritize fact domains plus concept families
3. Run deterministic fact extraction to normalize directly observable evidence
4. Use deterministic facts, including concept-evidence, to guide semantic atlas work
5. Produce atlas with failure_modes.detection for sauron consumption

## Design Workflow

1. Read requirements and constraints
2. Select frameworks and patterns from the semantic catalogs
3. Compose architecture with component topology
4. Produce atlas with full detection metadata and infrastructure stubs
