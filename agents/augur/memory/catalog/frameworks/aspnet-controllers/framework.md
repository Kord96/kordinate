---
description: ASP.NET Core controller-based API surface with attribute routing and controller classes
---
# ASP.NET Controllers

ASP.NET Controllers is the ASP.NET Core controller-based API surface with attribute routing and controller classes.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/aspnet-controllers/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- controller-bloat
- attribute-routing-fragmentation
- service-layer-sprawl
