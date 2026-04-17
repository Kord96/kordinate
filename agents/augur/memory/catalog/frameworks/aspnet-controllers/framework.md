---
description: ASP.NET Core controller-based API surface with attribute routing and controller classes
---
# ASP.NET Controllers

ASP.NET Controllers is the ASP.NET Core controller-based API surface with attribute routing and controller classes.

## Recognition
Use the detector package under `detectors/facts/frameworks/aspnet-controllers/` as the deterministic source of truth for framework evidence.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- controller-bloat
- attribute-routing-fragmentation
- service-layer-sprawl
