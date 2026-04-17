---
description: Swift server framework with route builders, grouped endpoints, and explicit application bootstrap
---
# Vapor

Vapor is a Swift server framework with route builders, grouped endpoints, and explicit application bootstrap.

## Recognition
Use the detector package under `detectors/facts/frameworks/vapor/` as the deterministic source of truth for framework evidence.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- route-builder-sprawl
- grouped-endpoint-coupling
- bootstrap-bloat
