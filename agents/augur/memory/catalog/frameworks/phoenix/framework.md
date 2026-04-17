---
description: Elixir web framework with router macros, channel support, and explicit endpoint pipelines
---
# Phoenix

Phoenix is an Elixir web framework with router macros, channel support, and explicit endpoint pipelines.

## Recognition
Use the detector package under `detectors/facts/frameworks/phoenix/` as the deterministic source of truth for framework evidence.

## Architectural implications
- framework scope: `backend`
- framework kind: `full-stack`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- pipeline-sprawl
- context-boundary-blur
- channel-controller-overlap
