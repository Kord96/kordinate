---
kind: framework
name: axum
signatures:
  framework: axum
  manifest_packages:
    cargo:
    - axum
  source_extensions:
  - .rs
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - Router::new\s*\(
    - \.route\s*\(
    medium:
    - axum::routing::(get|post|put|delete|patch)
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
language: rust
framework_kind: api-server
scope: backend
status: primary
family: frameworks
relationships:
  implements:
  - rest
  uses:
  - server-route-registration
traits:
  api_surface: true
  typed_handlers: true
common_failure_modes:
- router-sprawl
- extractor-coupling
- handler-bloat
---

# Explanation

Axum is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `memory/concepts/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector assets, when present, live under `detectors/concepts/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- router-sprawl
- extractor-coupling
- handler-bloat
