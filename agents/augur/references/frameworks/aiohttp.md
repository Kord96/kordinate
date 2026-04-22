---
kind: framework
name: aiohttp
signatures:
  framework: aiohttp
  manifest_packages:
    pyproject:
    - aiohttp
    requirements:
    - aiohttp
  source_extensions:
  - .py
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - from\s+aiohttp\s+import\s+web
    - web\.Application\s*\(
    medium:
    - router\.add_(get|post|put|delete|route)\s*\(
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
source:
  memory_framework: memory/catalog/frameworks/aiohttp/framework.md
  semantics: memory/catalog/frameworks/aiohttp/semantics.yaml
language: python
framework_kind: api-server
scope: backend
status: specialized
---

# Explanation

aiohttp is an async Python networking framework used for HTTP servers and clients built around the event loop.

## Recognition
Common signals:
- `from aiohttp import web`
- `web.Application()`
- `router.add_get(...)` or `router.add_route(...)`
- async request handlers returning `web.Response`

## Architectural implications
- request handling, client I/O, and lifecycle behavior are tightly coupled to async discipline
- route wiring is explicit but minimal
- application structure tends to be convention-driven rather than framework-enforced

## Common failure modes
- blocking I/O inside async handlers
- lifecycle hooks becoming ad hoc startup orchestration
- too much business logic living directly in request handlers
