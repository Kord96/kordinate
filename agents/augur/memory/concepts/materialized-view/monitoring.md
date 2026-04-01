---
description: Materialized View — monitoring guidance
type: supplementary
---
## Monitoring

Track view freshness, refresh performance, and query patterns to detect stale or degraded read models.

### Key Metrics

- `view_staleness_seconds` (gauge) — time since the last successful refresh
- `view_refresh_duration_seconds` (histogram) — how long each refresh cycle takes
- `view_refresh_failures_total` (counter) — failed refresh attempts
- `view_query_total` (counter) — queries served from the materialized view

### Alerts

- View staleness exceeding the defined freshness SLA
- Refresh duration growing over time (source data volume increasing or query plan degradation)
- Consecutive refresh failures (view becoming progressively stale)
- View query rate dropping to zero (consumers may have switched away or view is broken)
