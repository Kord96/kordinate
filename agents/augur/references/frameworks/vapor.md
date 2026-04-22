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
source:
  memory_framework: memory/catalog/frameworks/vapor/framework.md
  semantics: memory/catalog/frameworks/vapor/semantics.yaml
language: swift
framework_kind: api-server
scope: backend
status: specialized
---

# Explanation

Vapor is a Swift server framework with route builders, grouped endpoints, and explicit application bootstrap.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/vapor/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- route-builder-sprawl
- grouped-endpoint-coupling
- bootstrap-bloat
