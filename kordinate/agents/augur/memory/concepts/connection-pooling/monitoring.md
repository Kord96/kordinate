---
description: Connection Pooling — monitoring guidance
type: supplementary
---
## Monitoring

Track pool utilization, wait times, and connection health.

### Key Metrics

- `pool_active_connections` (gauge) — currently checked-out connections
- `pool_idle_connections` (gauge) — available connections in the pool
- `pool_wait_duration_seconds` (histogram) — time callers wait for an available connection
- `pool_timeout_total` (counter) — requests that timed out waiting for a connection

### Alerts

- Pool exhaustion: active connections at max with waiters queuing
- Connection wait time exceeding latency SLA
- High rate of stale connection evictions (upstream instability)
