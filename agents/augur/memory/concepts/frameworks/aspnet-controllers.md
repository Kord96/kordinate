---
kind: framework
name: aspnet-controllers
signatures:
  framework: aspnet-controllers
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
    - \[ApiController\]
    - \[Http(Get|Post|Put|Delete|Patch)\]
    medium:
    - ControllerBase
    - \[Route\("api/\[controller\]"\)\]
    weak: []
  negative_path_patterns: []
  negative_source_patterns:
  - WebApplication\.CreateBuilder\s*\(
  - app\.Map(Get|Post|Put|Delete|Patch)\s*\(
language: csharp
framework_kind: api-server
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
common_failure_modes:
- controller-bloat
- attribute-routing-fragmentation
- service-layer-sprawl
---

# Explanation

ASP.NET Controllers is the ASP.NET Core controller-based API surface with attribute routing and controller classes.

## Recognition
Use the framework reference in `memory/concepts/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector assets, when present, live under `detectors/concepts/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `api-server`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- controller-bloat
- attribute-routing-fragmentation
- service-layer-sprawl
