---
description: ASP.NET Core minimal API surface with builder-based startup and MapVerb route registration
---
# ASP.NET Minimal

ASP.NET Minimal is the ASP.NET Core minimal API surface with builder-based startup and `MapVerb` route registration.

## Recognition
Use the detector package under `detectors/facts/frameworks/aspnet-minimal/` as the deterministic source of truth for framework evidence.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- program-dot-cs-bloat
- route-handler-sprawl
- implicit-service-wiring
