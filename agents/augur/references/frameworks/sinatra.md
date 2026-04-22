---
kind: framework
name: sinatra
signatures:
  framework: sinatra
  manifest_packages:
    gemfile:
    - sinatra
  source_extensions:
  - .rb
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - require\s+['"]sinatra['"]
    - ^\s*(get|post|put|delete|patch)\s+[\'"]
    medium: []
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
source:
  memory_framework: memory/catalog/frameworks/sinatra/framework.md
  semantics: memory/catalog/frameworks/sinatra/semantics.yaml
language: ruby
framework_kind: api-server
scope: backend
status: specialized
---

# Explanation

Sinatra is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/sinatra/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- route-handler-bloat
- global-state-coupling
- inline-business-logic
