# Concept Catalog

Augur's vocabulary for understanding codebases. Each concept has recognition signatures that augur uses to detect what patterns, models, flows, and structures a codebase employs.

## Concept Types

| Type | Count | What it answers |
|------|-------|----------------|
| `pattern` | ~168 | How is this code built? (circuit-breaker, hexagonal, saga...) |
| `anti-pattern` | ~61 | What smells does this code have? (god-object, n-plus-one...) |
| `domain-model` | ~19 | What is this system? (ledger, catalog, graph, time-series...) |
| `flow-shape` | ~9 | How do things move through it? (request-path, fan-out, pipeline...) |
| `structure-shape` | ~6 | How are components organized? (layered, plugin-host, cell-based...) |

## File Structure

Each concept lives in its own file:

```
concepts/<name>.md  # canonical narrative: recognition signatures, confidence tiers, architecture notes
```

## Frontmatter

```yaml
description: One-line summary
type: pattern | anti-pattern | domain-model | flow-shape | structure-shape
abstraction: [category, category]    # e.g., [resilience, integration]
testable: true                       # optional — can be validated with automated checks
observable: true                     # optional — observable in running systems
distributed: true                    # optional — distributed systems concern
graphable: true                      # optional — can be meaningfully diagrammed
```

## How Augur Uses This

1. The index layer under `../../indexes/` is preloaded as stable ontology and navigation context.
2. During `/analyze`, Augur detects frameworks and concepts via deterministic assets under `../../../detectors/`.
3. `<name>.md` remains the canonical narrative for concept meaning, signatures, and architectural implications.
4. Detector policy and executable rules live under `../../../detectors/concepts/<name>/`.
5. Generated runtime bundles live under `../../../bundles/`.

## Indexes

- `../../indexes/concepts.md` — patterns + domain models + flow shapes + structure shapes
- `../../indexes/anti-patterns.md` — anti-patterns
- `../../indexes/abstractions.md` — abstraction levels for categorization
