---
description: Rate Limiting — testing guidance
type: supplementary
---
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
