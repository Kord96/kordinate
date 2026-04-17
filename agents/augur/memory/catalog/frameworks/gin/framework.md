---
description: Go web framework with explicit routing and middleware around HTTP handlers
---
# Gin

Gin is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the detector package under `detectors/facts/frameworks/gin/` as the deterministic source of truth for framework evidence.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- handler-bloat
- middleware-ordering-surprises
- global-engine-coupling
