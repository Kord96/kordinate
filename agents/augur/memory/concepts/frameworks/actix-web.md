---
kind: framework
name: actix-web
signatures:
  framework: actix-web
  manifest_packages:
    cargo:
    - actix_web
  source_extensions:
  - .rs
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - web::resource\s*\(
    - '#\[(get|post|put|delete|patch)\('
    medium:
    - App::new\s*\(
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
language: rust
framework_kind: api-server
scope: backend
status: specialized
family: frameworks
relationships:
  implements:
  - rest
  uses:
  - server-route-registration
traits:
  api_surface: true
  macro_routes_native: true
common_failure_modes:
- macro-indirection
- service-config-sprawl
- handler-bloat
---

# Explanation

Actix Web is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `memory/concepts/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/actix-web/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- macro-indirection
- service-config-sprawl
- handler-bloat
