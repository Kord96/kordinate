## Testing

Verify eviction order, cache correctness, and behavior under capacity and concurrency.

### Unit Tests

- Fill the cache to capacity, add one more entry, and assert the least-recently-used entry was evicted
- Access an entry to make it recently used, then fill the cache, and verify it survives eviction
- Verify cache keys are deterministic: equivalent inputs produce cache hits, not duplicate entries

### Concurrency Tests

- Access the cache from multiple threads simultaneously and verify no corrupted entries or lost updates
- Verify that concurrent reads and writes do not deadlock

### Edge Cases

- Test cache with `maxsize=1` and verify correct single-entry behavior
- Cache a mutable object, modify it externally, and verify the cache returns the original (defensive copy check)
- Verify TTL-based invalidation: entries expire after the configured duration

## Monitoring

Track hit rates, eviction frequency, and cache size to detect misconfigured capacity or degraded workloads.

### Key Metrics

- `cache_hit_total` / `cache_miss_total` (counters) — hit rate is the primary effectiveness signal
- `cache_evictions_total` (counter) — evictions due to capacity limit
- `cache_size` (gauge) — current number of entries in the cache
- `cache_lookup_duration_seconds` (histogram) — latency of cache get operations

### Alerts

- Hit rate dropping below an acceptable threshold (cache is not effective for the workload)
- Eviction rate spiking (cache too small for the working set)
- Cache size stuck at maximum with high eviction rate (capacity increase needed)
- Lookup latency increasing (potential lock contention or hash collision issues)

