---
kind: framework
name: fastify
signatures:
  framework: fastify
  manifest_packages:
    package_json:
    - fastify
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
    - require\(['"]fastify['"]\)
    - import\s+fastify\b
    - \bfastify\s*\(
    medium:
    - \bfastify\.(get|post|put|delete|patch|route)\s*\(
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
source:
  memory_framework: memory/catalog/frameworks/fastify/framework.md
  semantics: memory/catalog/frameworks/fastify/semantics.yaml
language: typescript
framework_kind: api-server
scope: backend
status: primary
---

# Explanation

Fastify is a high-performance Node.js web framework with schema-aware routes and plugin-driven composition.

## Recognition
Common signals:
- `require('fastify')` or `import fastify`
- `fastify(...)`
- `fastify.get(...)`, `fastify.post(...)`, or `fastify.route(...)`
- route schemas and plugin registration

## Architectural implications
- route schemas are a strong contract surface for validation and serialization
- plugin registration often becomes the composition root
- performance-oriented choices reward clear separation between handlers and business logic

## Common failure modes
- plugins hide too much wiring and lifecycle behavior
- route schemas drift from actual handler behavior
- business logic grows inside route handlers and hooks
