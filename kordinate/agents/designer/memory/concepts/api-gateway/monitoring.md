---
description: API Gateway — monitoring guidance
curated: true
scope: global
preloaded: none
---
## Monitoring

Track request routing, upstream health, and policy enforcement to detect gateway degradation and abuse.

### Key Metrics

- `gateway_request_duration_seconds` (histogram) — end-to-end request latency by route and upstream
- `gateway_upstream_errors_total` (counter) — upstream failures by backend service and error class
- `gateway_rate_limit_rejected_total` (counter) — requests rejected by rate limiting
- `gateway_auth_failures_total` (counter) — authentication/authorization failures by type
- `gateway_upstream_health` (gauge) — health status per upstream backend (1=healthy, 0=down)

### Alerts

- Upstream error rate exceeding threshold for any backend
- Rate-limit rejections spiking (potential abuse or misconfigured limits)
- Authentication failure rate increasing sharply (credential stuffing or misconfiguration)
- Gateway latency p99 exceeding SLA (upstream slowness or gateway overload)
