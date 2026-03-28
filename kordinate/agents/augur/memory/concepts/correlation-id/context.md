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

## Monitoring

Track correlation ID propagation completeness and use them to trace request flows.

### Key Metrics

- `requests_without_correlation_id_total` (counter) — requests missing a correlation ID (propagation gap)
- `correlation_hop_count` (histogram) — number of services a correlation ID traverses
- `trace_completeness_ratio` (gauge) — percentage of requests with full end-to-end correlation

### Alerts

- Correlation ID missing rate exceeding threshold (broken propagation in a service)
- Orphaned correlation IDs (started but no terminal service recorded completion)
- Duplicate correlation IDs generated (collision in ID generation)

## Deployment

Ensure all services propagate correlation IDs consistently, especially during mixed-version rollouts.

### Rollout Implications

- New services must propagate existing correlation IDs from incoming requests, not generate new ones
- During rolling updates, both old and new versions must handle the correlation header identically
- Log format changes must preserve the correlation ID field to maintain traceability across versions

### Pre-deploy Checklist

- Verify the correlation ID header name is consistent across all services in the call chain
- Confirm logging configuration includes the correlation ID in structured log fields

