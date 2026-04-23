---
kind: framework
name: koa
signatures:
  framework: koa
  manifest_packages:
    package_json:
    - koa
    - '@koa/router'
    - koa-router
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
    - require\(['"]koa['"]\)
    - import\s+Koa\b
    - \bnew\s+Koa\s*\(
    medium:
    - \brouter\.(get|post|put|delete|patch|use)\s*\(
    weak: []
  negative_path_patterns: []
  negative_source_patterns:
  - import\s+express\b
language: typescript
framework_kind: api-server
scope: backend
status: specialized
family: frameworks
relationships:
  implements:
  - rest
  supports:
  - middleware
  uses:
  - server-route-registration
traits:
  api_surface: true
  middleware_native: true
  async_native: true
common_failure_modes:
- middleware-ordering-surprises
- context-mutation-sprawl
- business-logic-in-routes
---

# Explanation

Koa is a middleware-oriented Node.js framework that emphasizes async composition and explicit request context handling.

## Recognition
Common signals:
- `import Koa` or `require('koa')`
- `new Koa()`
- router registration layered on top of middleware
- `ctx` mutation and async middleware chains

## Architectural implications
- the middleware pipeline is the dominant composition surface
- auth, validation, and response shaping often happen through stacked middleware
- architecture quality depends on keeping `ctx` usage and middleware responsibilities disciplined

## Common failure modes
- middleware order becomes implicit control flow
- request context turns into shared mutable state
- business logic leaks into middleware instead of staying in application services
