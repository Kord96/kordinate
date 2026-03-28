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

## Monitoring

Track request volume, latency distribution, and error rates by endpoint and HTTP method.

### Key Metrics

- `http_requests_total` (counter) -- request count by method, endpoint, and status code
- `http_request_duration_seconds` (histogram) -- latency distribution by endpoint
- `http_response_size_bytes` (histogram) -- response payload size by endpoint
- `http_4xx_total` (counter) -- client errors by endpoint (400, 404, 422, 429)
- `http_5xx_total` (counter) -- server errors by endpoint (500, 502, 503)

### Alerts

- 5xx error rate exceeds threshold for any endpoint (server-side failure)
- P99 latency exceeds SLA for a sustained period (performance degradation)
- 429 rate spike on authentication endpoints (possible brute-force or credential stuffing)
- Sudden drop in request volume on a high-traffic endpoint (upstream failure or routing change)

