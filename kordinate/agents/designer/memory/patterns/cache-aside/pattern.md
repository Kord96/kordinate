---
description: Cache-Aside architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
---
# Cache-Aside

## Recognition

How to identify this pattern in code.

### Signatures

- Check cache first, on miss load from source, then populate cache before returning
- TTL (time-to-live) configuration on cached entries
- Cache key generation functions or key templates
- Redis or Memcached client calls with fallback to database queries
- `@cache` or `@cached` decorators with expiration parameters
- Pattern: `get from cache -> if nil -> fetch from DB -> set in cache -> return`
- Cache invalidation on write paths: `cache.delete(key)` after updates

### Confidence

- **high** -- explicit check-cache/load-source/populate-cache flow with TTL configuration
- **medium** -- caching decorator or middleware with automatic key generation
- **low** -- manual in-memory dict used as a cache with no eviction policy

## Architecture

Look for a read path that tries cache first and falls back to the source of truth, with explicit cache population and invalidation.

### Review Checklist

- Cache miss path correctly populates the cache before returning the result
- TTLs are set appropriately for the data's staleness tolerance
- Cache invalidation happens on every write path that modifies the cached data
- Cache key collisions are prevented (namespaced, versioned, or hashed keys)
- Thundering herd is mitigated (locking, request coalescing, or stale-while-revalidate)
- Serialization format is versioned to survive schema changes

### Anti-patterns

- Forgetting to invalidate cache on write (serving stale data indefinitely)
- Cache keys without namespacing leading to collisions across entities
- No TTL set, relying entirely on manual invalidation (cache grows unbounded)
- Caching errors or empty results (negative caching without short TTL)
