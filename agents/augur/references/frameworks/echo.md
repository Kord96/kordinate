---
kind: framework
name: echo
signatures:
  framework: echo
  manifest_packages:
    go_mod:
    - github.com/labstack/echo
  source_extensions:
  - .go
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - echo\.New\s*\(
    medium:
    - \be\.(GET|POST|PUT|DELETE|PATCH)\s*\(
    - \be\.Group\s*\(
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
source:
  memory_framework: memory/catalog/frameworks/echo/framework.md
  semantics: memory/catalog/frameworks/echo/semantics.yaml
language: go
framework_kind: api-server
scope: backend
status: primary
---

# Explanation

Echo is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/echo/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- handler-bloat
- middleware-ordering-surprises
- context-coupling
