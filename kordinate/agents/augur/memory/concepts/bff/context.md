## Testing

Test response aggregation, client-specific shaping, and graceful degradation when upstream services fail.

### Unit Tests

- Verify response shape matches the contract expected by the target client (web, mobile, etc.)
- Test aggregation logic: multiple upstream responses are merged into the correct BFF response
- Assert that unnecessary fields are stripped and client-specific transformations are applied

### Integration Tests

- Wire the BFF against stubbed upstream services and verify end-to-end response assembly
- Test with multiple BFF variants (web, mobile) against the same upstreams to verify different output shapes

### Failure Injection

- Take down one upstream and verify the BFF returns a partial response with degradation markers rather than a full failure

## Monitoring

Track per-client BFF response times, upstream aggregation latency, and error rates.

### Key Metrics

- `bff_request_duration_seconds` (histogram) — end-to-end latency per BFF endpoint and client type
- `bff_upstream_calls_total` (counter) — calls to backend services per BFF request
- `bff_upstream_latency_seconds` (histogram) — latency of individual upstream calls
- `bff_errors_total` (counter) — errors by type (upstream failure, transformation error)

### Alerts

- BFF latency exceeding client-specific SLA
- Upstream service failure rate causing degraded BFF responses
- Disproportionate error rate on one client-specific BFF versus others

## Deployment

Each BFF can be deployed independently, but coordinate with client release schedules.

### Rollout Implications

- BFF changes may need to align with mobile app releases — old clients may call deprecated BFF endpoints
- Deploy BFF updates before or alongside the client that depends on new response shapes
- Multiple BFF instances can coexist — version endpoints to support gradual client migration

### Pre-deploy Checklist

- Verify backward compatibility with the oldest supported client version
- Confirm upstream service dependencies are available in the target environment

