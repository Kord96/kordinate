---
description: Kotlin server framework with routing DSLs and explicit application module setup
---
# Ktor

Ktor is a Kotlin server framework with routing DSLs and explicit application module setup.

## Recognition
Use the detector package under `detectors/facts/frameworks/ktor/` as the deterministic source of truth for framework evidence.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- routing-dsl-sprawl
- plugin-config-fragmentation
- handler-bloat
