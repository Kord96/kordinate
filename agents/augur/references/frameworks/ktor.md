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
source:
  memory_framework: memory/catalog/frameworks/ktor/framework.md
  semantics: memory/catalog/frameworks/ktor/semantics.yaml
language: kotlin
framework_kind: api-server
scope: backend
status: specialized
---

# Explanation

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
