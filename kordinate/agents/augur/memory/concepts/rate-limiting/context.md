## Testing

Verify correct enforcement at configured thresholds, proper header responses, and behavior when the limit store is unavailable.

### Unit Tests

- Send exactly the limit number of requests and verify all succeed, then send one more and verify 429 response
- Verify rate limit headers in the response: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`
- Test window reset: after the time window elapses, verify the client can make requests again
- Verify different endpoints have independent limits (hitting the limit on one does not affect another)

### Algorithm Tests

- Test the specific algorithm (token bucket, sliding window, fixed window) boundary behavior at window edges
- Verify per-client isolation: one client hitting its limit does not affect other clients
- Test with burst traffic: send all allowed requests at once and verify the limiter enforces the correct shape

### Integration Tests

- Deploy multiple replicas with a shared Redis store and verify global limits are enforced (not per-instance)
- Simulate Redis unavailability and verify the limiter fails open or closed as configured
- Test with realistic traffic patterns and verify the rejection rate matches expectations

## Monitoring

Track limit enforcement, rejection rates, and per-client usage to tune thresholds and detect abuse.

### Key Metrics

- `rate_limit_requests_total` (counter) -- total requests evaluated by the rate limiter, by endpoint
- `rate_limit_rejected_total` (counter) -- requests rejected with 429, by client/API key and endpoint
- `rate_limit_remaining` (gauge) -- remaining quota per client in the current window
- `rate_limit_latency_seconds` (histogram) -- overhead added by rate limit evaluation (should be sub-millisecond)

### Alerts

- Rejection rate exceeds threshold for a specific client (possible abuse or misconfigured integration)
- Global rejection rate spikes across all clients (may indicate limits set too low for legitimate traffic)
- Rate limit store (Redis) latency increases (degraded shared state lookup slowing all requests)
- Rate limit evaluation latency exceeds acceptable overhead (middleware performance issue)

## Deployment

Ensure rate limit state is shared across replicas and limits are tuned for the new deployment's capacity.

### Rollout Implications

- Distributed rate limiting requires a shared store (Redis); verify the store is accessible from all new pods before cutover
- Scaling up replicas does not automatically increase per-client limits -- limits are global, not per-instance
- Scaling down replicas does not reduce throughput capacity if limits are correctly shared
- Changing limit values should be deployable independently from application code (config or feature flags)

### Pre-deploy Checklist

- Verify the shared rate limit store (Redis) is healthy and reachable from the target environment
- Confirm rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`) are returned for 429 responses
- Review per-endpoint limits: authentication endpoints should have stricter limits than read-only endpoints
- Test that the rate limiter fails open or closed as intended when the shared store is unavailable

