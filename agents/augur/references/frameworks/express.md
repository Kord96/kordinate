---
kind: framework
name: express
signatures:
  framework: express
  manifest_packages:
    package_json:
    - express
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
    - require\(['"]express['"]\)
    - import\s+express\b
    - \bexpress\s*\(
    medium:
    - \bapp\.(get|post|put|delete|patch|use)\s*\(
    - \brouter\.(get|post|put|delete|patch|use)\s*\(
    weak: []
  negative_path_patterns: []
  negative_source_patterns:
  - '@Controller\b'
source:
  memory_framework: memory/catalog/frameworks/express/framework.md
  semantics: memory/catalog/frameworks/express/semantics.yaml
language: typescript
framework_kind: api-server
scope: backend
status: primary
---

# Explanation

Express is a minimal Node.js web framework built around middleware chains and explicit route registration.

## Recognition
Common signals:
- `require('express')` or `import express`
- `express()`
- `app.get(...)`, `app.post(...)`, or `router.use(...)`
- middleware stacks handling auth, parsing, and error flow

## Architectural implications
- middleware order is a first-class runtime concern
- route boundaries are easy to expose but easy to overload with business logic
- typing and validation quality depend on local conventions and libraries

## Common failure modes
- route handlers swallowing orchestration and business logic
- implicit middleware ordering causing auth or error regressions
- weak request/response typing allowing contract drift
