---
description: Rate Limiting — deployment guidance
type: supplementary
---
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
