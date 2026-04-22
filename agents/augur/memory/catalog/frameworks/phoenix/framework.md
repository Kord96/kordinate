---
description: Elixir web framework with router macros, channel support, and explicit endpoint pipelines
---
# Phoenix

Phoenix is an Elixir web framework with router macros, channel support, and explicit endpoint pipelines.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/phoenix/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `full-stack`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- pipeline-sprawl
- context-boundary-blur
- channel-controller-overlap
