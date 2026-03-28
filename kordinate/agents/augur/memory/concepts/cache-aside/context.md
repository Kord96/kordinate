## Testing

Verify the read-through and invalidation lifecycle: miss populates, hit returns cached, write invalidates.

### Unit Tests

- First read for a key misses cache, fetches from origin, and populates cache
- Second read for the same key returns cached data without hitting origin
- After a write/update, verify the cache entry is invalidated and the next read fetches fresh data

### Integration Tests

- Wire against real cache (Redis/Memcached) and origin database, verify full read-write-invalidate cycle
- Test TTL expiration: verify stale entries are evicted and subsequent reads re-fetch from origin

### Failure Injection

- Simulate cache unavailability and verify the application falls through to the origin database gracefully

## Monitoring

Track cache hit rates, latency impact, and staleness indicators.

### Key Metrics

- `cache_hits_total` (counter) — cache hit count by key prefix or resource type
- `cache_misses_total` (counter) — misses that trigger a database read and cache fill
- `cache_fill_latency_seconds` (histogram) — time to fetch from origin and populate cache
- `cache_evictions_total` (counter) — entries evicted by TTL or capacity pressure

### Alerts

- Cache hit rate dropping below baseline (possible misconfiguration or key-space change)
- Cache fill latency spike (origin database degradation)
- Eviction rate spike indicating undersized cache

