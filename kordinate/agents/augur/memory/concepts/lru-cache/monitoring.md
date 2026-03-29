---
description: LRU Cache — monitoring guidance
type: supplementary
---
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
