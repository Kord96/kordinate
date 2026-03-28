---
description: LRU Cache architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [data, infrastructure]
---
# LRU Cache

## Recognition

How to identify this pattern in code.

### Signatures

- `@lru_cache` or `functools.lru_cache` decorator in Python
- `LinkedHashMap` with `accessOrder=true` in Java
- `maxsize` or `capacity` parameter limiting cache entries
- Eviction of least-recently-used entry when cache is full
- Cache hit/miss tracking (`cache_info()`, hit rate metrics)
- `LRUCache`, `LruCache` class names or doubly-linked list + hash map combination
- `@Cacheable` with eviction policy in Spring
- Node.js `lru-cache` or `quick-lru` packages

**Not this pattern (Python):** A single `@lru_cache` on a utility function for memoization (e.g., `@lru_cache(maxsize=None)` on a pure function) is standard Python optimization, not the LRU cache architectural pattern. The pattern is about using LRU eviction as an architectural caching strategy -- multiple cached data access points, explicit capacity management, cache invalidation on writes. One `@lru_cache` decorator is Python idiom, not architecture.

### Confidence

- **high** -- Bounded cache with explicit LRU eviction, `maxsize` configuration, and hit/miss tracking across multiple call sites
- **medium** -- `@lru_cache` decorator or `LinkedHashMap` used on multiple strategic caching points without explicit eviction monitoring
- **low** -- Dictionary/map used as a cache with manual size checks that may implement LRU

## Architecture

Look for correct bounded caching with O(1) lookup and eviction, and appropriate cache invalidation.

### Review Checklist

- `maxsize` is tuned for the workload -- not set arbitrarily or left at defaults
- Cache keys are deterministic and produce consistent hashes for equivalent inputs
- Cache invalidation strategy exists (TTL, explicit invalidation, or versioned keys)
- Hit/miss ratio is tracked and observable via metrics or logging
- Mutable objects are not cached without defensive copies (aliasing bugs)
- Thread safety is addressed for concurrent access (thread-safe wrapper or per-thread caches)

### Anti-patterns

- Unbounded cache masquerading as LRU (missing `maxsize`, grows until OOM)
- Caching mutable objects that callers later modify (corrupted cache entries)
- No invalidation strategy -- stale data served indefinitely
- Using LRU cache for items with uniform access frequency (no temporal locality to exploit)
