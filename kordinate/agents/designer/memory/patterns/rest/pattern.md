---
description: REST API architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
---
# REST API

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
