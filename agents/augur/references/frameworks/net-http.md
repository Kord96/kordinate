---
kind: framework
name: net-http
signatures:
  framework: net-http
  manifest_packages: {}
  source_extensions:
  - .go
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - import\s+"net/http"
    - http\.HandleFunc\s*\(
    - http\.ListenAndServe\s*\(
    medium:
    - http\.NewServeMux\s*\(
    - mux\.Handle\s*\(
    weak: []
  negative_path_patterns: []
  negative_source_patterns:
  - gin\.Default\s*\(
  - chi\.NewRouter\s*\(
  - echo\.New\s*\(
  - fiber\.New\s*\(
source:
  memory_framework: memory/catalog/frameworks/net-http/framework.md
  semantics: memory/catalog/frameworks/net-http/semantics.yaml
language: go
framework_kind: api-server
scope: backend
status: supporting
---

# Explanation

net/http is the standard Go HTTP server surface built from handlers, mux wiring, and listen/serve entrypoints.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/net-http/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- handler-bloat
- ad-hoc-middleware
- implicit-routing-sprawl
