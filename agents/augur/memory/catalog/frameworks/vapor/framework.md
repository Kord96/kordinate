---
description: Swift server framework with route builders, grouped endpoints, and explicit application bootstrap
---
# Vapor

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
