---
description: Request path flow note; prefer router or server-route-registration for the route surface itself
type: flow-shape
abstraction: [api, integration]
status: supporting
scope: backend
relationships:
  related_to: [server-route-registration, middleware]
---
# Request Path

Treat this as a supporting end-to-end flow note, not a primary routing concept.

- Use [router](/concepts/router) for frontend navigation routing.
- Use [server-route-registration](/concepts/server-route-registration) for backend route declaration and exposure.
- Use this concept when the important question is the request's path across layers and components after routing has already been resolved.

## Recognition

### Signatures

- HTTP route handler calling a service layer which calls a repository/data layer
- Middleware chain: auth → validation → handler → response serialization
- Express `app.get()` → controller → service → repository chain
- FastAPI `@app.get()` → dependency injection → service → ORM
- Spring `@RestController` → `@Service` → `@Repository`
- Go `http.HandleFunc` → handler → service → store
- Request/response DTOs at API boundary, domain models internally
- Error handling middleware that catches and formats responses

### Confidence

- **high** — clear layered handler chain: route → middleware → controller → service → repository → database, with DTOs at boundaries
- **medium** — handler calls service which calls database, but without clean layering or DTOs
- **low** — handler directly queries database with no service layer
