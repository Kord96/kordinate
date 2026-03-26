---
description: Backend for Frontend — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
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
