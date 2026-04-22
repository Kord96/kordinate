---
kind: framework
name: chi
signatures:
  framework: chi
  manifest_packages:
    go_mod:
    - github.com/go-chi/chi
  source_extensions:
  - .go
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - chi\.NewRouter\s*\(
    medium:
    - \br\.(Get|Post|Put|Delete|Patch)\s*\(
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
source:
  memory_framework: memory/catalog/frameworks/chi/framework.md
  semantics: memory/catalog/frameworks/chi/semantics.yaml
language: go
framework_kind: api-server
scope: backend
status: specialized
---

# Explanation

Chi is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/chi/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- router-sprawl
- middleware-ordering-surprises
- implicit-subrouter-boundaries
