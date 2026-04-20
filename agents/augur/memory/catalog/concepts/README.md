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

Detector coverage is optional.

- some concepts are semantics-only ontology entries with no deterministic detector package yet
- when a concept has deterministic coverage, it lives under `../../../detectors/facts/concept-evidence/<name>/`
- semantic meaning still lives here even when no detector package exists yet

## Frontmatter

```yaml
description: One-line summary
type: pattern | anti-pattern | domain-model | flow-shape | structure-shape
abstraction: [category, category]    # e.g., [resilience, integration]
testable: true                       # optional — can be validated with automated checks
observable: true                     # optional — observable in running systems
distributed: true                    # optional — distributed systems concern
graphable: true                      # optional — can be meaningfully diagrammed
status: primary | specialized | supporting | compatibility   # optional — ontology role
scope: frontend | backend | cross-cutting | domain | platform # optional — where the concept applies most
relationships:                        # optional — explicit ontology edges
  is_a: [broader-concept]
  part_of: [parent-concept]
  related_to: [peer-concept]
  preferred_over: [less-preferred-concept]
  disambiguates: [often-confused-concept]
  implements: [pattern-or-contract]
  supports: [capability-or-pattern]
  uses: [dependency-or-surface]
```

## How Augur Uses This

1. The index layer under `../../indexes/` is preloaded as stable ontology and navigation context.
2. During `/analyze`, Augur detects frameworks and concept evidence via deterministic assets under `../../../detectors/facts/`.
3. `<name>.md` remains the canonical narrative for concept meaning, signatures, and architectural implications.
4. When present, detector policy and executable rules live under `../../../detectors/facts/concept-evidence/<name>/`.
5. The ontology graph is generated from concept and framework source metadata into `../../indexes/ontology-graph.json` and `../../indexes/ontology-graph.md`.
6. Generated runtime bundles live under `../../../.generated/bundles/`.
7. Concept frontmatter is the canonical source for concept-to-concept ontology edges. Framework semantics may author framework-origin edges to concepts, but should not redefine concept-to-concept relationships.

## Split Of Responsibilities

- `concepts/<name>.md`
  Canonical meaning: what the concept is, how to recognize it semantically, and why it matters architecturally.
- `detectors/facts/concept-evidence/<name>/`
  Deterministic evidence policy: signatures, executable rules, review questions, and monitoring hints for concepts that have detector support.

## Relationship Semantics

- `is_a`
  Specialized concept -> broader concept.
- `part_of`
  Constituent or sub-technique -> parent concept.
- `related_to`
  Peer relationship with no hierarchy. Use sparingly.
- `preferred_over`
  Editorial preference edge. Add it only when Augur should bias toward one concept framing over another.
- `disambiguates`
  Use when one concept clarifies a commonly confused neighboring concept.
- `implements`
  Technology or framework -> pattern or contract it realizes.
- `supports`
  Technology or framework -> capability or pattern it natively supports.
- `uses`
  Directed dependency or surface usage edge.

## Indexes

- `../../indexes/concepts.md` — patterns + domain models + flow shapes + structure shapes
- `../../indexes/anti-patterns.md` — anti-patterns
- `../../indexes/abstractions.md` — abstraction levels for categorization
