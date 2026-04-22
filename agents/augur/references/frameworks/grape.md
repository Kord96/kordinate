---
kind: framework
name: grape
signatures:
  framework: grape
  manifest_packages:
    gemfile:
    - grape
  source_extensions:
  - .rb
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - Grape::API
    - resource\s+:\w+
    medium:
    - ^\s*(get|post|put|delete|patch)\s+:\w+
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
source:
  memory_framework: memory/catalog/frameworks/grape/framework.md
  semantics: memory/catalog/frameworks/grape/semantics.yaml
language: ruby
framework_kind: api-server
scope: backend
status: specialized
---

# Explanation

Grape is a Ruby API framework centered on declarative endpoint DSLs and resource blocks.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/grape/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- endpoint-dsl-sprawl
- resource-block-bloat
- validation-logic-fragmentation
