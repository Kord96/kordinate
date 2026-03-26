---
description: Correlation ID — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify end-to-end ID propagation, generation at the edge, and presence in logs and responses.

### Unit Tests

- Send a request without a correlation ID and verify the edge service generates one
- Send a request with an existing correlation ID and verify it is preserved, not replaced
- Assert the correlation ID appears in all log entries for the request

### Integration Tests

- Trace a request across multiple services and verify the same correlation ID appears in every service's logs
- Verify the correlation ID is included in the response headers for client-side tracing
- Test async flows: verify the correlation ID propagates through message queues and background jobs

### Failure Injection

- Remove the correlation ID middleware from one service and verify monitoring detects the propagation gap
