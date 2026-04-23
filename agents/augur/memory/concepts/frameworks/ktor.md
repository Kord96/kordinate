---
kind: framework
name: ktor
signatures:
  framework: ktor
  manifest_packages:
    pom:
    - io.ktor
  source_extensions:
  - .kt
  - .kts
  - .gradle
  - .xml
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - embeddedServer\s*\(
    - routing\s*\{\s*get\(
    medium:
    - io\.ktor
    - route\s*\(\s*"/
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
language: kotlin
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
  async_native: true
common_failure_modes:
- routing-dsl-sprawl
- plugin-config-fragmentation
- handler-bloat
---

# Explanation

Ktor is a Kotlin server framework with routing DSLs and explicit application module setup.

## Recognition
Use the framework reference in `memory/concepts/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector assets, when present, live under `detectors/concepts/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- routing-dsl-sprawl
- plugin-config-fragmentation
- handler-bloat
