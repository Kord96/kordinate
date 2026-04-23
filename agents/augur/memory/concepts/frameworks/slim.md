---
kind: framework
name: slim
signatures:
  framework: slim
  manifest_packages:
    composer:
    - slim/slim
  source_extensions:
  - .php
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - \$app->(get|post|put|delete|patch|group)\s*\(
    medium: []
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
language: php
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
  middleware_native: true
common_failure_modes:
- route-handler-bloat
- middleware-ordering-surprises
- container-coupling
---

# Explanation

Slim is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `memory/concepts/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/slim/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- route-handler-bloat
- middleware-ordering-surprises
- container-coupling
