---
kind: framework
name: phoenix
signatures:
  framework: phoenix
  manifest_packages:
    mix_exs:
    - phoenix
  source_extensions:
  - .ex
  - .exs
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - use\s+\w+Web,\s*:router
    - 'pipe_through\s+:'
    medium:
    - resources\s+"/
    - scope\s+"/
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
language: elixir
framework_kind: full-stack
scope: backend
status: primary
family: frameworks
relationships:
  implements:
  - rest
  uses:
  - server-route-registration
traits:
  api_surface: true
  realtime_native: true
common_failure_modes:
- pipeline-sprawl
- context-boundary-blur
- channel-controller-overlap
---

# Explanation

Phoenix is an Elixir web framework with router macros, channel support, and explicit endpoint pipelines.

## Recognition
Use the framework reference in `memory/concepts/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/phoenix/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `full-stack`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- pipeline-sprawl
- context-boundary-blur
- channel-controller-overlap
