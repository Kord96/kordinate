---
kind: concept
name: cache-aside
signatures:
  concept: cache-aside
  positive:
    strong:
    - explicit cache-first, source-on-miss, repopulate-on-return flow
    - TTL-backed cache population with write-side invalidation
    medium:
    - caching decorators or wrappers with clear miss-fill behavior
    weak:
    - ad-hoc in-memory cache checks with unclear invalidation
  negative:
  - write paths never clear or refresh cached keys
  - cache used as the source of truth rather than an aside
  notes:
  - Distinguish this from read-through or write-behind, which imply different ownership
    of cache logic.
type: pattern
abstraction:
- data
- resilience
scope: domain
status: primary
review_questions:
  threshold: 5
  entries:
  - id: cache-aside-miss-fill
    prompt: Does the read path check cache first, then load from the source of truth,
      then repopulate the cache?
    weight: 3
    signals:
    - .get(
    - setex
    - cached(ttl=
  - id: cache-aside-write-invalidation
    prompt: Do writes invalidate or refresh the same cache keys rather than leaving
      stale entries behind?
    weight: 2
    signals:
    - del(
    - invalidate
    - ttl
monitoring:
  applies_to:
  - component
  - dependency
  - flow
  health_signals:
  - name: cache.hit.rate
    description: Fraction of reads served from cache without going to the source of
      truth.
  - name: cache.miss.latency
    description: End-to-end latency for cache-miss paths that refill from the source.
  - name: cache.invalidation.error.rate
    description: Failures invalidating or refreshing keys after writes.
  business_metrics: []
  gaps:
  - Without hit-rate and invalidation visibility, cache correctness and value are
    hard to judge.
family: design-patterns
---

# Explanation

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

### Relationship To Other Concepts

- Related to [repository](/concepts/repository) when repositories coordinate reads through a cache before falling back to a primary store.
- Related to [search-index](/concepts/search-index) when cached query results or projections reduce repeated expensive lookups.
- Related to [write-behind](/concepts/write-behind) as a different cache persistence strategy where writes are deferred rather than reads being populated on miss.

### Boundary

Use `cache-aside` when the application explicitly checks a cache first, loads from the source on miss, and then populates the cache.

Do not use it for any caching. The important signal is the miss-path population pattern controlled by the application or repository layer.
