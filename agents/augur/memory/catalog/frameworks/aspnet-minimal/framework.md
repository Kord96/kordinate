---
description: ASP.NET Core minimal API surface with builder-based startup and MapVerb route registration
---
# ASP.NET Minimal

ASP.NET Minimal is the ASP.NET Core minimal API surface with builder-based startup and `MapVerb` route registration.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/aspnet-minimal/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- program-dot-cs-bloat
- route-handler-sprawl
- implicit-service-wiring
