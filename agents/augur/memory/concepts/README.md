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

Each concept lives in its own directory:

```
concepts/<name>/
  concept.md       # canonical narrative: recognition signatures, confidence tiers, architecture notes
  meta.yaml        # optional structured companion: detector policy, questions, and structured ops guidance
  ast-grep.yaml    # optional support artifact for structural detection
  semgrep.yaml     # optional support artifact for semantic/security detection
  questions.yaml   # legacy optional diagnostic questions during migration to meta.yaml
  testing.md       # legacy optional testing guidance during migration to meta.yaml
  monitoring.md    # legacy optional monitoring guidance during migration to meta.yaml
  deployment.md    # legacy optional deployment guidance during migration to meta.yaml
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

1. The concept index files are preloaded on boot; individual concept directories are read on demand.
2. During `/analyze`, augur detects concepts via an evidence-first flow: broad grep → AST/semgrep → signature verification → diagnostic questions.
3. `concept.md` remains the canonical narrative for concept meaning, signatures, and confidence notes.
4. `meta.yaml` is the canonical structured source for detector policy, diagnostic questions, and testing/monitoring/deployment guidance when present.
5. `ast-grep.yaml` and `semgrep.yaml` remain separate support artifacts.

## Indexes

- `../concepts.md` — patterns + domain models + flow shapes + structure shapes
- `../anti-patterns.md` — anti-patterns
- `../abstractions.md` — abstraction levels for categorization
