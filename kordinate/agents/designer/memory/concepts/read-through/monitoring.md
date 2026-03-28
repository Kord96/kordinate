---
description: Read-Through Cache — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
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
