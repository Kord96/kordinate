---
description: Cache Stampede Prevention architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [data, resilience, concurrency]
---
# Cache Stampede Prevention

## Recognition

How to identify this pattern in code.

### Signatures

- Lock-based cache population (only one thread/process recomputes on miss)
- `singleflight` package (Go) coalescing concurrent requests for the same key
- Probabilistic early recomputation (XFetch algorithm)
- Request coalescing for identical in-flight cache loads
- `SETNX` or `SET NX` for distributed cache locks
- `@CachePut` with locking or mutex around the computation
- Semaphore or mutex guarding cache population code paths

### Confidence

- **high** -- `singleflight.Group.Do()` or explicit mutex/lock around cache-miss computation with other requesters waiting
- **medium** -- `SETNX`-based distributed lock for cache population, or probabilistic early recomputation logic
- **low** -- Short TTLs with staggered expiry that reduce but do not eliminate stampede risk

## Architecture

Look for coordination mechanisms that ensure only one caller recomputes a cache entry while others wait or receive a stale value.

### Review Checklist

- Lock holder timeout prevents deadlock if the computing thread crashes
- Waiters have a bounded timeout and fallback (do not block indefinitely)
- Lock granularity is per-key, not global (avoids serializing unrelated cache misses)
- Stale-while-revalidate is used where acceptable to serve old values during recomputation
- Distributed lock cleanup handles node failures (TTL on the lock key itself)
- Probabilistic early recomputation parameters are tuned to the access pattern

### Anti-patterns

- Global lock for all cache misses, serializing unrelated keys
- No timeout on the lock, causing permanent blocking if the holder crashes
- Every caller independently recomputes on miss without coordination (the stampede itself)
- Lock without retry or fallback, causing callers to fail instead of waiting
