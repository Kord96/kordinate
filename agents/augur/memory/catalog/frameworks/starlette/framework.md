---
description: ASGI toolkit for Python services with explicit routes, middleware, and async request handling
---
# Starlette

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
