---
description: Rate Limiting — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
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
