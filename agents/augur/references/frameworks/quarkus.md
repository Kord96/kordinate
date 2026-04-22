---
kind: framework
name: quarkus
signatures:
  framework: quarkus
  manifest_packages:
    pom:
    - quarkus
  source_extensions:
  - .java
  - .kt
  - .xml
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - '@Path\s*\('
    - '@GET\b'
    - '@POST\b'
    - '@PUT\b'
    medium:
    - quarkus
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
source:
  memory_framework: memory/catalog/frameworks/quarkus/framework.md
  semantics: memory/catalog/frameworks/quarkus/semantics.yaml
language: java
framework_kind: api-server
scope: backend
status: specialized
---

# Explanation

Quarkus is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/quarkus/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- annotation-heavy-indirection
- build-time-magic
- runtime-assumption-coupling
