---
description: Augur workflow — analyze existing code or design new projects, producing atlas as primary output
---
# Workflow

## Skills

| Skill | Purpose |
|-------|---------|
| `/analyze` | Analyze existing codebases — pattern detection, debt assessment, failure modes |
| `/design` | Design new projects (4 modes: full, api, service, component) |

## Primary Output: Atlas

The atlas is the primary output consumed by all agents (charon, sauron, alfred). It contains:
- Components and their connections
- Failure modes with structured detection metadata (signals, concerns, source patterns)
- Infrastructure requirements (vitals config, dashboard stubs, resource defaults)
- Dependency map

See `schemas/atlas-schema.md` for the full schema.

## Knowledge Base

- **Concept catalog** (265 patterns) at `memory/concepts/` — `concept.md` stays canonical, while `meta.yaml` carries detector policy and structured ops guidance where migrated
- **Infra-atlas** at `/kord/agents/charon/memory/global/infra-atlas.json` — cluster topology, observability endpoints, workload contract
- **App contract** at `memory/app-contract.md` — requirements every deployed app must satisfy

## Analyze Workflow

1. Gather source code and identify frameworks (check imports, not project name)
2. Match against concept catalog for recognized patterns
3. Assess debt, detect anti-patterns, review structure
4. Produce atlas with failure_modes.detection for sauron consumption

## Design Workflow

1. Read requirements and constraints
2. Select patterns from concept catalog
3. Compose architecture with component topology
4. Produce atlas with full detection metadata and infrastructure stubs
