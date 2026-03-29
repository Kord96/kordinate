---
description: Refresh-Ahead Cache — monitoring guidance
type: supplementary
---
## Monitoring

Track refresh success rates, stale-serve frequency, and background thread pool health.

### Key Metrics

- `cache_refresh_total` (counter) -- background refresh attempts, by cache name
- `cache_refresh_errors_total` (counter) -- failed refresh attempts (backing source timeout, error)
- `cache_stale_serves_total` (counter) -- requests served from a stale entry while refresh is in progress
- `cache_refresh_latency_seconds` (histogram) -- time to complete a background refresh from the source
- `cache_refresh_pool_active` (gauge) -- active threads in the refresh executor pool

### Alerts

- Refresh error rate exceeds threshold (backing source degraded, risk of entries expiring without replacement)
- Stale-serve rate spikes (refreshes not completing before TTL, callers getting outdated data)
- Refresh thread pool saturated (all threads busy, queued refreshes backing up)
- Refresh latency exceeds the gap between refresh interval and TTL (entries may expire before refresh completes)
