---
description: Java framework ecosystem with annotation-driven controllers, dependency injection, and broad infrastructure integration
---
# Spring

Spring is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the detector package under `detectors/facts/frameworks/spring/` as the deterministic source of truth for framework evidence.

## Architectural implications
- framework scope: `backend`
- framework kind: `full-stack`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- annotation-heavy-indirection
- service-layer-bloat
- hidden-runtime-magic
