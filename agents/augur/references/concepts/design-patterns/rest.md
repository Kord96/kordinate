---
kind: concept
name: rest
signatures:
  concept: rest
  positive:
    strong:
    - resource-oriented URLs with semantic HTTP methods and status codes
    - OpenAPI or Swagger contracts describing resource endpoints
    medium:
    - mostly resource-shaped JSON APIs with some consistent HTTP semantics
    weak:
    - generic HTTP JSON APIs that may still be RPC-over-HTTP
  negative:
  - action-oriented URLs like /getUser or /createOrder
  - POST used for every operation regardless of intent
  notes:
  - REST should stay candidate until semantic review confirms method and URL discipline.
source:
  memory_concept: memory/catalog/concepts/rest.md
type: pattern
abstraction:
- api
- integration
scope: backend
status: primary
review_questions:
  threshold: 6
  entries:
  - id: rest-resource-oriented-surface
    prompt: Does the public server surface organize URLs around resources rather than
      action verbs?
    weight: 3
    signals:
    - GET
    - POST
    - /users
  - id: rest-method-and-status-semantics
    prompt: Are HTTP method semantics and status-code usage part of the contract rather
      than just HTTP transport for RPC?
    weight: 3
    signals:
    - 201
    - 204
    - OpenAPI
monitoring:
  applies_to:
  - flow
  - component
  health_signals:
  - name: http.4xx_5xx.rate
    description: Error-rate visibility for REST endpoints grouped by resource or route.
  business_metrics: []
  gaps:
  - REST requires semantic review of route and status conventions; AST matches alone
    are not sufficient.
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- HTTP methods mapped to CRUD operations (GET=read, POST=create, PUT/PATCH=update, DELETE=delete)
- Resource-based URL paths: `/users`, `/users/123`, `/users/123/orders`
- HTTP status codes used semantically (200, 201, 204, 400, 404, 409, 422)
- JSON request/response bodies with content-type `application/json`
- OpenAPI/Swagger specification files (`openapi.yaml`, `swagger.json`)
- HATEOAS links in responses (`_links`, `href`)
- Versioning in URL path (`/v1/`, `/v2/`) or headers (`Accept: application/vnd.api.v1+json`)

### Confidence

- **high** -- resource-based URLs with correct HTTP method semantics, OpenAPI spec, proper status codes
- **medium** -- JSON API with URL patterns that suggest resources but methods may be overloaded (POST for everything)
- **low** -- HTTP endpoints returning JSON but URLs are action-based (`/getUser`, `/createOrder`) rather than resource-based

## Architecture

Look for resource-oriented URL design with correct HTTP method semantics and meaningful status codes.

### Relationship To Other Concepts

- `rest` is the API style: resource-oriented URLs, HTTP semantics, and status-code discipline.
- Use `server-route-registration` for the mechanics of exposing handlers.
- Use `pagination` for list traversal strategy.
- Prefer `graphql` when clients query graph-shaped data through a schema rather than fixed resource endpoints.

### Review Checklist

- URLs represent resources (nouns), not actions (verbs)
- HTTP methods match their intended semantics (GET is safe and idempotent, PUT is idempotent)
- Status codes are used correctly (not 200 for everything with error details in the body)
- Pagination is implemented for list endpoints (cursor-based or offset/limit)
- API versioning strategy is consistent across all endpoints
- Error responses follow a consistent format with actionable messages

### Anti-patterns

- Using POST for all operations regardless of intent (RPC-over-HTTP)
- Returning 200 OK for error conditions with error details only in the response body
- Deeply nested resource URLs beyond two levels (`/a/1/b/2/c/3/d/4`)
- No pagination on list endpoints that can return unbounded results

### Boundary

Do not use `rest` for any JSON-over-HTTP service. Prefer it only when resource semantics and HTTP method discipline are clear architectural choices.

### Relationship To Other Concepts

- Related to [graphql](/concepts/graphql) as an alternative API style where clients shape graph queries instead of navigating resource-oriented endpoints.
- Related to [pagination](/concepts/pagination) because list and collection resources require explicit paging semantics.
- Related to [server-route-registration](/concepts/server-route-registration) because RESTful services are exposed through concrete server route declarations.
