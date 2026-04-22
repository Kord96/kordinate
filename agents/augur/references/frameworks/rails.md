---
kind: framework
name: rails
signatures:
  framework: rails
  manifest_packages:
    gemfile:
    - rails
  source_extensions:
  - .rb
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - Rails\.application\.routes\.draw\b
    - ^\s*resources\s+:\w+
    medium:
    - ^\s*namespace\s+:\w+
    - ^\s*scope\s+[\'"]/
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
source:
  memory_framework: memory/catalog/frameworks/rails/framework.md
  semantics: memory/catalog/frameworks/rails/semantics.yaml
language: ruby
framework_kind: full-stack
scope: backend
status: primary
---

# Explanation

Rails is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/rails/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `full-stack`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- fat-models
- callback-heavy-control-flow
- implicit-convention-coupling
