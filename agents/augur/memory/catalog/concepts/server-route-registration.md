---
description: Backend route declaration and exposure for HTTP or RPC handlers
type: pattern
graphable: true
abstraction:
- api
- integration
status: primary
scope: backend
relationships:
  disambiguates:
  - router
  related_to:
  - request-path
  - middleware
  - rest
  - graphql
  - grpc
aliases: []
disambiguates_from:
- router
preferred_over: []
implies: []
anti_signals: []
detector_coverage: rich
examples: []
---
# Server Route Registration

## Recognition

How to identify this pattern in code.

### Signatures

- Route decorators or registration calls binding methods and paths to handlers
- `app.get()`, `router.post()`, `Route(...)`, `path(...)`, `http.HandleFunc(...)`
- FastAPI, Flask, Express, NestJS, Django, Spring, ASP.NET, or Go HTTP server registration APIs
- RPC service registration for server handlers when the code exposes a service contract to clients
- Per-route middleware, guards, or dependency injection attached at declaration time

### Confidence

- **high** -- framework route declaration APIs bind methods or subjects directly to handlers with explicit path or service registration
- **medium** -- route declaration is spread across controller metadata, config, or router modules but still clearly registers externally reachable handlers
- **low** -- handler-like functions exist but exposure is indirect or inferred only from naming

## Architecture

Use this concept when the code defines the public server surface itself: which handlers are reachable, under what path or service name, and with what route-level policies.

### Review Checklist

- Route definitions are centralized enough to understand the public surface without scanning every handler body
- Route-level middleware, auth, validation, and serialization concerns are visible at or near registration time
- Server routes expose stable resource or procedure contracts rather than ad-hoc handler wiring
- Versioning, tags, or grouping make the public surface discoverable

### Anti-patterns

- Route exposure scattered across dynamic registration code with no visible public surface
- Handler registration hidden behind reflection or naming magic with no route manifest
- Public routes with inconsistent auth, validation, or error handling conventions

### Relationship To Other Concepts

- Disambiguates from [router](/concepts/router), which should remain a frontend navigation concept.
- Related to [middleware](/concepts/middleware) when per-route or shared request interception is attached at registration time.
- Related to [rest](/concepts/rest), [graphql](/concepts/graphql), and [grpc](/concepts/grpc) because route or service registration is how those APIs are exposed on the server side.

### Boundary

Use `server-route-registration` when the important signal is backend declaration of HTTP or RPC handlers and exposure of server endpoints.

Do not use it for client-side URL navigation. If the main concern is view switching or frontend navigation, use [router](/concepts/router).
