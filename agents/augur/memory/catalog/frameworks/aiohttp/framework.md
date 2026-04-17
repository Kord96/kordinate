---
description: Async Python networking framework for HTTP services and clients built around the event loop
---
# aiohttp

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
