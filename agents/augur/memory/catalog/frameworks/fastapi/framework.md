# FastAPI

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
