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
  concept.md       # recognition signatures, confidence tiers, architecture notes
  ast-grep.yaml    # optional — AST rule for structural pattern detection
  semgrep.yaml     # optional — semgrep rule for security/error anti-patterns
  questions.yaml   # optional — diagnostic questions for ambiguous detection
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

1. All concept files are **preloaded on boot** (~12% of context window)
2. During `/analyze`, augur detects concepts via 4-pass scanning (grep → AST tools → signature verification → diagnostic questions)
3. Detected concepts inform component annotation, debt scoring, flow tracing, and story composition
4. The `type` field tells augur how to use each concept: patterns are implementation techniques, domain-models describe data shapes, flow-shapes describe data movement, structure-shapes describe organization

## Indexes

- `../concepts.md` — patterns + domain models + flow shapes + structure shapes
- `../anti-patterns.md` — anti-patterns
- `../abstractions.md` — abstraction levels for categorization
