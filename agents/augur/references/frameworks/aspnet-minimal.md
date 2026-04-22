---
kind: framework
name: aspnet-minimal
signatures:
  framework: aspnet-minimal
  manifest_packages:
    csproj:
    - Microsoft.AspNetCore
  source_extensions:
  - .cs
  - .csproj
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - WebApplication\.CreateBuilder\s*\(
    - app\.Map(Get|Post|Put|Delete|Patch)\s*\(
    medium:
    - builder\.Services\.
    weak: []
  negative_path_patterns: []
  negative_source_patterns:
  - \[ApiController\]
  - ControllerBase
source:
  memory_framework: memory/catalog/frameworks/aspnet-minimal/framework.md
  semantics: memory/catalog/frameworks/aspnet-minimal/semantics.yaml
language: csharp
framework_kind: api-server
scope: backend
status: primary
---

# Explanation

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
