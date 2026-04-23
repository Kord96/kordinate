---
kind: concept
name: request-path
signatures: {}
type: flow-shape
abstraction:
- api
- integration
scope: backend
status: supporting
family: flow-shapes
---

# Explanation

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

### Relationship To Other Concepts

- Related to [router](/concepts/router) because this concept commonly appears alongside it or is clarified by contrast with it.

### Boundary

Use `request-path` when the important observation is this specific flow or payload shape within a backend service, storage, or server-side architectural concern.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
