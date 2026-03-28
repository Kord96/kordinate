## Testing

Verify pool lifecycle, bounded concurrency, and correct connection reuse behavior.

### Unit Tests

- Acquire and release a connection — verify it returns to the pool for reuse
- Acquire connections up to the max pool size and verify the next request waits or times out
- Test idle eviction: leave a connection idle beyond the TTL and verify it is closed and replaced

### Integration Tests

- Run concurrent workloads through the pool against a real database and verify no connection leaks
- Test pool warm-up: verify minimum connections are established at startup

### Failure Injection

- Kill the database server and verify the pool detects dead connections, evicts them, and reconnects when the server recovers

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

