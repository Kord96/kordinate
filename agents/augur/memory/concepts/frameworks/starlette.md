---
kind: framework
name: starlette
signatures:
  framework: starlette
  manifest_packages:
    requirements:
    - starlette
  source_extensions:
  - .py
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - from\s+starlette
    - \bStarlette\s*\(
    medium:
    - \bRoute\s*\(
    - \bMount\s*\(
    weak: []
  negative_path_patterns: []
  negative_source_patterns:
  - from\s+fastapi\s+import
language: python
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
  async_native: true
  middleware_native: true
common_failure_modes:
- mixed-sync-async
- middleware-ordering-surprises
- hand-rolled-validation
---

# Explanation

Starlette is a lower-level ASGI framework for Python services with explicit routes, middleware, and async request handling.

## Recognition
Common signals:
- `from starlette...` imports
- `Starlette(...)`
- `Route(...)` and `Mount(...)`
- ASGI middleware and response primitives

## Architectural implications
- the framework exposes the request pipeline more directly than batteries-included stacks
- route and middleware boundaries are usually explicit
- application architecture quality depends heavily on local conventions

## Common failure modes
- mixed sync and async boundaries causing latency or deadlocks
- middleware ordering hiding auth or error-handling behavior
- validation and serialization scattered across handlers
