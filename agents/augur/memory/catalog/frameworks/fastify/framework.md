---
description: High-performance Node.js web framework with schema-aware routes and plugin-driven composition
---
# Fastify

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
