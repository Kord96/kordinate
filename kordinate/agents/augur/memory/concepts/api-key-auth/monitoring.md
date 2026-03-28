---
description: API Key Authentication — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track authentication outcomes, key usage patterns, and abuse signals.

### Key Metrics

- `api_auth_requests_total` (counter) — authentication attempts by outcome (success, invalid, expired)
- `api_key_usage_total` (counter) — requests per API key for usage tracking
- `api_auth_latency_seconds` (histogram) — time spent validating keys
- `api_rate_limit_exceeded_total` (counter) — rate limit hits per key

### Alerts

- Spike in invalid key attempts (potential credential stuffing)
- Single key exceeding rate limits repeatedly
- Expired key still receiving traffic (client misconfiguration)
