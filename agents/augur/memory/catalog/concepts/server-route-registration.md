---
description: Backend route declaration and exposure for HTTP or RPC handlers
type: pattern
graphable: true
abstraction: [api, integration]
status: primary
scope: backend
relationships:
  disambiguates: [router]
  related_to: [request-path, middleware, rest, graphql, grpc]
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

- Prefer [router](/concepts/router) for frontend navigation routing.
- Prefer `server-route-registration` when the code is wiring backend HTTP or RPC handlers.
- Use [request-path](/concepts/request-path) when the important question is the end-to-end path after the route has already been matched.
