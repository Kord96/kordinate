---
kind: framework
name: symfony
signatures:
  framework: symfony
  manifest_packages:
    composer:
    - symfony/framework-bundle
  source_extensions:
  - .php
  - .yaml
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - '#\[Route\('
    - '@Route\('
    medium:
    - framework-bundle
    - config/routes\.yaml
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
  dependency_injection_native: true
  validation_native: true
common_failure_modes:
- service-graph-indirection
- annotation-or-attribute-sprawl
- config-fragmentation
---

# Explanation

Symfony is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `memory/concepts/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/symfony/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `full-stack`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- service-graph-indirection
- annotation-or-attribute-sprawl
- config-fragmentation
