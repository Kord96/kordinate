---
kind: framework
name: hono
signatures:
  framework: hono
  manifest_packages:
    package_json:
    - hono
  source_extensions:
  - .js
  - .jsx
  - .ts
  - .tsx
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - import\s+\{\s*Hono\s*\}
    - \bnew\s+Hono\s*\(
    medium:
    - \bapp\.(get|post|put|delete|patch|route)\s*\(
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
language: typescript
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
  edge_runtime_friendly: true
common_failure_modes:
- route-handler-sprawl
- edge-runtime-assumptions
- middleware-ordering-surprises
---

# Explanation

Hono is a lightweight web framework for JavaScript runtimes with fluent route registration and middleware composition.

## Recognition
Common signals:
- `import { Hono }`
- `new Hono()` or `const app = new Hono()`
- `app.get(...)`, `app.post(...)`, or `app.route(...)`
- deployment targets oriented toward edge or lightweight runtimes

## Architectural implications
- route registration is explicit and compact
- middleware and runtime-target assumptions matter more than heavy framework structure
- service architecture quality depends on keeping handlers thin and runtime boundaries explicit

## Common failure modes
- route handlers absorb orchestration logic
- edge-runtime assumptions leak into domain code
- middleware ordering hides cross-cutting behavior
