---
kind: framework
name: fastapi
signatures:
  framework: fastapi
  manifest_packages:
    pyproject:
    - fastapi
    requirements:
    - fastapi
  source_extensions:
  - .py
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - from\s+fastapi\s+import
    - import\s+fastapi
    - \bFastAPI\s*\(
    - \bAPIRouter\s*\(
    medium:
    - '@\w+\.(get|post|put|delete|patch|options|head)\s*\('
    - \bDepends\s*\(
    - \bBaseModel\b
    weak: []
  negative_path_patterns: []
  negative_source_patterns:
  - from\s+flask\s+import
  - from\s+django\.urls\s+import
language: python
framework_kind: api-server
scope: backend
status: primary
family: frameworks
relationships:
  implements:
  - rest
  supports:
  - dependency-injection
  - input-validation
  uses:
  - server-route-registration
  related_to:
  - layered
  - hexagonal
traits:
  api_surface: true
  async_native: true
  validation_native: true
  dependency_injection_native: true
common_concepts:
- repository
common_failure_modes:
- business-logic-in-routes
- mixed-sync-async
- leaking-persistence-models
---

# Explanation

FastAPI is an async Python web API framework centered on typed request/response models, declarative routing, and dependency injection.

## Recognition
Common signals:
- `from fastapi import FastAPI`
- `app = FastAPI()`
- `APIRouter()`
- route decorators like `@app.get`, `@router.post`
- Pydantic models for request/response validation

## Architectural implications
- API boundary validation is often framework-native
- request lifecycle is explicit and async-aware
- dependency injection is commonly used for repositories, services, auth, and DB sessions
- route handlers may stay thin, or may accumulate business logic if architecture is weak

## Common co-occurring concepts
- Repository
- Thin route handlers are common in stronger layered or hexagonal codebases, but not guaranteed by the framework

## Ontology position
- Implements REST-style API contracts
- Uses server-side route registration as its public surface
- Supports dependency injection and input validation natively
- Commonly co-occurs with layered or hexagonal application structure, but does not require either

## Common failure modes
- business logic in route handlers
- leaking ORM/session objects through the API layer
- implicit dependency wiring that hides boundaries
- mixed sync/async I/O causing latency or deadlocks
