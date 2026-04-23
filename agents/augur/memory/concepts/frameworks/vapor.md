---
kind: framework
name: vapor
signatures:
  framework: vapor
  manifest_packages:
    package_swift:
    - vapor/vapor
  source_extensions:
  - .swift
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - app\.(get|post|put|delete|patch)\s*\(
    medium:
    - app\.grouped\s*\(
    - import\s+Vapor
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
language: swift
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
common_failure_modes:
- route-builder-sprawl
- grouped-endpoint-coupling
- bootstrap-bloat
---

# Explanation

Vapor is a Swift server framework with route builders, grouped endpoints, and explicit application bootstrap.

## Recognition
Use the framework reference in `memory/concepts/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector assets, when present, live under `detectors/concepts/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- route-builder-sprawl
- grouped-endpoint-coupling
- bootstrap-bloat
