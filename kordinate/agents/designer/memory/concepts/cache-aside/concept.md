---
description: Cache-Aside architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [data, resilience]
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
- Java: `@Cacheable`, `@CacheEvict`, `CacheManager` (Spring Cache), Caffeine `Cache.get(key, loader)`, Guava `LoadingCache`
- Go: `groupcache`, `bigcache`, `ristretto`, `go-cache` imports
- Python: `cachetools`, `diskcache`, `dogpile.cache` libraries

### Negative signals (not sufficient for detection)

- The word `cache` alone (e.g., internal data structure caches, CPU cache references, freelist caches in databases) is NOT cache-aside. Look for cache-then-source read flow with TTL or invalidation.
- Internal implementation caches (e.g., `map` used as lookup cache inside a data structure, `LRUCache` for page management in a DB engine) are LRU-cache, not the cache-aside application pattern.
- Build/dependency caches (Gradle cache, npm cache, Docker layer cache) are tooling, not the pattern.
- Python: `@lru_cache` or `functools.cache` on pure functions for memoization is lru-cache, not cache-aside. Cache-aside requires a separate cache store (Redis, Memcached, external cache) with explicit check-load-populate flow against a backing data source.
- Python: `redis.get()` used for session storage or pub/sub is not cache-aside unless paired with a database fallback pattern.
- TypeScript: `Cache` API, `Map`-based caches for storing request responses, or React query caching (`useQuery`) are not cache-aside unless there is an explicit check-then-load-then-populate flow against a separate data source. Client-side request caching libraries (alova, SWR, React Query) implement stale-while-revalidate, not cache-aside.
- An in-memory `Map` or object used to store computed values without a backing data source is memoization, not cache-aside.

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
