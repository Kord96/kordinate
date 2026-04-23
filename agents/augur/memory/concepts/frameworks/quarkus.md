---
kind: framework
name: quarkus
signatures:
  framework: quarkus
  manifest_packages:
    pom:
    - quarkus
  source_extensions:
  - .java
  - .kt
  - .xml
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - '@Path\s*\('
    - '@GET\b'
    - '@POST\b'
    - '@PUT\b'
    medium:
    - quarkus
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
language: java
framework_kind: api-server
scope: backend
status: specialized
family: frameworks
relationships:
  implements:
  - rest
  supports:
  - dependency-injection
  uses:
  - server-route-registration
traits:
  api_surface: true
  dependency_injection_native: true
common_failure_modes:
- annotation-heavy-indirection
- build-time-magic
- runtime-assumption-coupling
---

# Explanation

Quarkus is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `memory/concepts/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector assets, when present, live under `detectors/concepts/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- annotation-heavy-indirection
- build-time-magic
- runtime-assumption-coupling
