---
description: Bulkhead — monitoring guidance
curated: true
scope: global
preloaded: none
---
## Monitoring

Track per-pool utilization and rejection rates to detect resource exhaustion before it cascades.

### Key Metrics

- `bulkhead_pool_active` (gauge) — currently active slots per pool
- `bulkhead_pool_available` (gauge) — remaining capacity per pool
- `bulkhead_rejections_total` (counter) — requests rejected due to pool exhaustion
- `bulkhead_wait_duration_seconds` (histogram) — time spent waiting for a pool slot

### Alerts

- Pool utilization consistently above 80% (approaching exhaustion)
- Rejection rate exceeding threshold for any single pool
- Wait duration p99 exceeding acceptable latency (pool undersized)
- Multiple pools exhausting simultaneously (systemic resource pressure)
