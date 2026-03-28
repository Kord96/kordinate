## Testing

Verify proactive refresh triggers before expiry, async execution, and correct fallback behavior on refresh failure.

### Unit Tests

- Populate a cache entry, advance time past the refresh threshold but before TTL, and verify a background refresh is triggered
- Verify the caller receives the stale cached value immediately while the refresh executes asynchronously
- After refresh completes, verify the next read returns the fresh value
- Simulate a refresh failure and verify the existing cached value is retained (not evicted)

### Timing Tests

- Verify refresh interval is shorter than TTL: entries are always refreshed before they would naturally expire
- Access a cold key (no recent reads) and verify it is not refreshed (only hot keys trigger refresh-ahead)
- Advance time past TTL without any access and verify the entry expires normally

### Concurrency Tests

- Trigger refresh from multiple concurrent readers and verify the backing source is called only once per refresh cycle
- Verify the refresh thread pool is bounded: saturate it and confirm excess refreshes are queued, not spawned unboundedly
- Test shutdown: stop the cache and verify all pending refreshes complete or are cancelled cleanly

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

