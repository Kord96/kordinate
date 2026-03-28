---
description: Cache-Aside — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
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
