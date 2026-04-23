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
language: go
framework_kind: api-server
scope: backend
status: specialized
family: frameworks
relationships:
  implements:
  - rest
  supports:
  - middleware
  uses:
  - server-route-registration
traits:
  api_surface: true
  middleware_native: true
common_failure_modes:
- router-sprawl
- middleware-ordering-surprises
- implicit-subrouter-boundaries
---

# Explanation

Chi is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `memory/concepts/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/chi/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- router-sprawl
- middleware-ordering-surprises
- implicit-subrouter-boundaries
