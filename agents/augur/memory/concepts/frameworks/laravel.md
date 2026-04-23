---
kind: framework
name: laravel
signatures:
  framework: laravel
  manifest_packages:
    composer:
    - laravel/framework
  source_extensions:
  - .php
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - Route::(get|post|put|delete|patch|resource|apiResource)\s*\(
    medium:
    - Illuminate\\Foundation
    - \bartisan\b
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
language: php
framework_kind: full-stack
scope: backend
status: primary
family: frameworks
relationships:
  implements:
  - rest
  supports:
  - dependency-injection
  - input-validation
  uses:
  - server-route-registration
  related_to:
  - layered
traits:
  api_surface: true
  orm_native: true
  validation_native: true
  dependency_injection_native: true
common_concepts:
- active-record
common_failure_modes:
- fat-controllers
- hidden-service-container-dependencies
- model-leakage
---

# Explanation

Laravel is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `memory/concepts/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector assets, when present, live under `detectors/concepts/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `full-stack`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- fat-controllers
- hidden-service-container-dependencies
- model-leakage
