---
description: Refresh-Ahead Cache architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [data, resilience]
---
# Refresh-Ahead Cache

## Recognition

How to identify this pattern in code.

### Signatures

- Proactive cache refresh before TTL expiry
- Background refresh threads or async reload tasks
- `refreshAfterWrite` configuration (Caffeine, Guava)
- Probabilistic early expiration (cache entries refreshed before nominal TTL)
- Cache warming on startup or scheduled pre-population
- Separate refresh executor or thread pool for async reloads
- Entries served stale while refresh is in progress

### Confidence

- **high** -- `refreshAfterWrite` with an async reload function, or explicit background thread refreshing entries before expiry
- **medium** -- Scheduled cache warming jobs that periodically repopulate hot keys
- **low** -- Short TTLs with frequent cache misses that approximate refresh-ahead behavior without explicit implementation

## Architecture

Look for a cache that proactively refreshes entries before they expire, ensuring callers always get a cache hit.

### Review Checklist

- Refresh executes asynchronously and does not block the caller serving the stale value
- Refresh thread pool is bounded to prevent resource exhaustion under heavy load
- Failed refreshes keep the existing cached value rather than evicting it
- Only hot keys are refreshed (cold keys are allowed to expire normally)
- Refresh interval is shorter than TTL to guarantee overlap

### Anti-patterns

- Synchronous refresh that blocks callers, negating the latency benefit
- Refreshing all cached keys regardless of access frequency (wasted resources)
- No fallback when the refresh source is unavailable, causing cache entries to expire with no replacement
- Unbounded refresh thread pool that can saturate the backing data source
