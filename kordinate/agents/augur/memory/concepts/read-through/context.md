## Testing

Verify transparent load-on-miss behavior, correct TTL eviction, and graceful handling of loader failures.

### Unit Tests

- Request a key not in cache, verify the loader is called, and the value is returned and cached
- Request the same key again and verify the loader is not called (cache hit)
- Wait for TTL expiry, request the key, and verify the loader is called again (stale eviction)
- Verify the loader is called with the correct key and parameters

### Failure Handling Tests

- Simulate a loader failure and verify the cache does not cache the error (no negative caching of exceptions)
- Verify a failed load for one key does not affect cached values for other keys
- Test bulk loading: request multiple keys in a batch and verify the loader is called once for all missing keys

### Concurrency Tests

- Request the same uncached key from multiple threads simultaneously and verify the loader is called only once (stampede protection)
- Verify concurrent reads of cached keys do not block each other
- Test cache warming on startup: verify pre-populated keys are served from cache without loader calls

## Monitoring

Track cache hit rates, loader performance, and miss storms to ensure the cache is providing value.

### Key Metrics

- `cache_hit_rate` (gauge) -- ratio of cache hits to total lookups (target: >90% for hot data)
- `cache_miss_total` (counter) -- cache misses triggering a loader call, by cache name
- `cache_load_latency_seconds` (histogram) -- time to load a value from the backing source on miss
- `cache_evictions_total` (counter) -- entries evicted by TTL or capacity pressure
- `cache_error_total` (counter) -- loader failures (backing source errors, timeouts)

### Alerts

- Cache hit rate drops below baseline (data pattern change, cache sized too small, or TTL too short)
- Cache load latency exceeds threshold (backing source degraded, impacting miss penalty)
- Spike in cache misses across many keys simultaneously (thundering herd on cold start or mass eviction)
- Loader error rate exceeds threshold (backing source unavailable, risk of serving stale data or errors)

