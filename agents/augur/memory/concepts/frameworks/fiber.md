---
kind: framework
name: fiber
signatures:
  framework: fiber
  manifest_packages:
    go_mod:
    - github.com/gofiber/fiber
  source_extensions:
  - .go
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - fiber\.New\s*\(
    medium:
    - \bapp\.(Get|Post|Put|Delete|Patch)\s*\(
    - \bapp\.Group\s*\(
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
language: go
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
  middleware_native: true
common_failure_modes:
- handler-bloat
- middleware-ordering-surprises
- express-style-overuse
---

# Explanation

Fiber is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `memory/concepts/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector assets, when present, live under `detectors/concepts/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- handler-bloat
- middleware-ordering-surprises
- express-style-overuse
