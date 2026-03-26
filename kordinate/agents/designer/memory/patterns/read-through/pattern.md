---
description: Read-Through Cache architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
---
# Read-Through Cache

## Recognition

How to identify this pattern in code.

### Signatures

- Cache that loads from the backing source automatically on miss (vs cache-aside where the caller loads)
- Cache-as-data-source pattern where callers only interact with the cache
- `CacheLoader` interface implementations
- Guava `LoadingCache` or `CacheBuilder.newBuilder().build(loader)`
- Caffeine `Caffeine.newBuilder().build(loader)`
- `@Cacheable` annotation with implicit load-on-miss behavior
- Cache provider configured with a read-through loader function

### Confidence

- **high** -- `CacheLoader` or `LoadingCache` with explicit loader function, or cache configured as the sole data access layer
- **medium** -- `@Cacheable` annotations where the framework handles loading transparently
- **low** -- Manual cache-aside code where the load logic is tightly coupled to the cache check (looks like read-through but is caller-managed)

## Architecture

Look for a cache layer that transparently loads data from the source on a miss, hiding the backing store from callers.

### Review Checklist

- Loader function handles source failures gracefully (no caching of error responses)
- Cache eviction policy matches data volatility (TTL appropriate for freshness requirements)
- Bulk loading is supported for batch access patterns, not just single-key lookups
- Cache warming strategy exists for cold starts to avoid a thundering herd on first access
- Null/missing values are handled explicitly (negative caching or passthrough)

### Anti-patterns

- Caching error responses or exceptions from the loader, serving stale errors to subsequent callers
- No TTL or eviction, causing the cache to serve stale data indefinitely
- Caller bypassing the cache to hit the source directly, defeating the read-through contract
- Loader function with side effects beyond data retrieval
