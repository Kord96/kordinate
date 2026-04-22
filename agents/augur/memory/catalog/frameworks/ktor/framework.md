---
description: Kotlin server framework with routing DSLs and explicit application module setup
---
# Ktor

Ktor is a Kotlin server framework with routing DSLs and explicit application module setup.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/ktor/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- routing-dsl-sprawl
- plugin-config-fragmentation
- handler-bloat
