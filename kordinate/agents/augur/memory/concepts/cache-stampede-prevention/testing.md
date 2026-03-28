---
description: Cache Stampede Prevention — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify that concurrent cache misses for the same key produce exactly one origin fetch.

### Unit Tests

- Expire a cache key and send N concurrent requests — assert only one origin fetch occurs
- Verify all N waiters receive the same recomputed value once the single fetch completes
- Test lock timeout: if the recomputing request hangs, waiters eventually fall through or receive an error

### Integration Tests

- Wire against real cache and origin, expire a hot key, and verify origin query count equals 1 under load
- Test probabilistic early recompute (XFetch): verify refresh happens before TTL, avoiding any stampede window

### Failure Injection

- Kill the holder of the recompute lock mid-fetch and verify waiters recover rather than deadlock
