---
description: REST API — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify correct HTTP semantics, resource-oriented design, and consistent error responses across all endpoints.

### Unit Tests

- Test each endpoint returns the correct HTTP status code (200, 201, 204, 400, 404, 409, 422)
- Verify GET requests are safe and idempotent (no side effects, same result on repeated calls)
- Verify PUT requests are idempotent (repeated PUTs with the same body produce the same state)
- Test validation: send invalid payloads and verify 400/422 with a structured error response

### Contract Tests

- Validate responses against the OpenAPI spec (schema compliance, required fields, correct types)
- Test pagination on list endpoints: verify correct page metadata, ordering, and boundary behavior
- Verify HATEOAS links (if used) point to valid endpoints and contain correct resource URLs
- Test API versioning: requests to deprecated versions return appropriate responses or redirects

### Integration Tests

- Run the full CRUD lifecycle (POST, GET, PUT, DELETE) for each resource and verify state transitions
- Test content negotiation: verify the API returns the correct content type based on the Accept header
- Verify error response format is consistent across all endpoints (same structure for 4xx and 5xx errors)
