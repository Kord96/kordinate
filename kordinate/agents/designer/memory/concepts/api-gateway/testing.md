---
description: API Gateway — testing guidance
curated: true
scope: global
preloaded: none
---
## Testing

Verify routing rules, cross-cutting policy enforcement, and graceful handling of upstream failures.

### Unit Tests

- Test routing rules: given a request path and method, assert it routes to the correct upstream backend
- Verify auth enforcement — requests with missing or invalid tokens are rejected before reaching any backend
- Test rate limiting logic: assert that requests exceeding the configured limit receive 429 responses
- Verify request/response transformation rules produce the expected output format

### Integration Tests

- Send requests through the gateway to real backend services and verify end-to-end routing correctness
- Test auth + rate limiting together: authenticated requests within limits succeed; over-limit requests are throttled regardless of valid auth
- Verify gateway behavior with multiple backends — route to each and confirm correct upstream selection under load

### Failure Injection

- Take a backend service down and verify the gateway returns a meaningful error (502/503) rather than hanging
- Simulate slow backend responses and verify gateway timeouts fire, returning errors to clients within SLA
- Kill the auth service and verify the gateway's fail-open or fail-closed policy matches its configuration
