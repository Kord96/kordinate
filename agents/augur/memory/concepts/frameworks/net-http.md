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
language: go
framework_kind: api-server
scope: backend
status: supporting
family: frameworks
relationships:
  implements:
  - rest
  uses:
  - server-route-registration
traits:
  api_surface: true
  standard_library: true
common_failure_modes:
- handler-bloat
- ad-hoc-middleware
- implicit-routing-sprawl
---

# Explanation

net/http is the standard Go HTTP server surface built from handlers, mux wiring, and listen/serve entrypoints.

## Recognition
Use the framework reference in `memory/concepts/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/net-http/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- handler-bloat
- ad-hoc-middleware
- implicit-routing-sprawl
