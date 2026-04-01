---
description: Request path flow — synchronous request through a handler chain with response
type: flow-shape
abstraction: [api, integration]
---
# Request Path

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
