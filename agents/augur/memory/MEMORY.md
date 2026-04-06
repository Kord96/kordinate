# Augur memory

Augur's source memory is organized into:

- `catalog/` — semantic source of truth for frameworks and concepts
- `indexes/` — compact navigational indexes and ontology summaries
- `contracts/` — normative architectural requirements
- `workspace/` — local working notes, not canonical knowledge

Generated runtime artifacts live outside this source tree under `../bundles/`.

## Source memory
- [workflow.md](workflow.md) — Augur review and analysis workflow
- [tools.md](tools.md) — Tooling reference for analysis and validation
- [catalog/concepts/README.md](catalog/concepts/README.md) — Concept catalog structure and semantics/detector split
- [indexes/concepts.md](indexes/concepts.md) — Pattern and domain-model index
- [indexes/anti-patterns.md](indexes/anti-patterns.md) — Anti-pattern index
- [indexes/abstractions.md](indexes/abstractions.md) — Abstraction ontology
- [contracts/app-contract.md](contracts/app-contract.md) — Application contract

## Generated bundles
- `../bundles/memory/` — model-facing compiled memory bundles
- `../bundles/detectors/` — generated detector execution bundles

## Detector source
Detector policy and executable rule assets live under `../detectors/`, separated from semantic memory.
