---
kind: framework
name: symfony
signatures:
  framework: symfony
  manifest_packages:
    composer:
    - symfony/framework-bundle
  source_extensions:
  - .php
  - .yaml
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - '#\[Route\('
    - '@Route\('
    medium:
    - framework-bundle
    - config/routes\.yaml
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
source:
  memory_framework: memory/catalog/frameworks/symfony/framework.md
  semantics: memory/catalog/frameworks/symfony/semantics.yaml
language: php
framework_kind: full-stack
scope: backend
status: primary
---

# Explanation

Symfony is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/symfony/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `full-stack`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- service-graph-indirection
- annotation-or-attribute-sprawl
- config-fragmentation
