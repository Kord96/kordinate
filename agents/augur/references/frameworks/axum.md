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
source:
  memory_framework: memory/catalog/frameworks/axum/framework.md
  semantics: memory/catalog/frameworks/axum/semantics.yaml
language: rust
framework_kind: api-server
scope: backend
status: primary
---

# Explanation

Axum is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/axum/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- router-sprawl
- extractor-coupling
- handler-bloat
