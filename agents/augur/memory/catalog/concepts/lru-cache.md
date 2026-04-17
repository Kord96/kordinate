---
description: LRU Cache architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction:
- data
- infrastructure
status: primary
scope: domain
relationships:
  related_to:
  - cache-aside
  - read-through
  - key-value-model
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
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

### Confidence

- **high** -- Bounded cache with explicit LRU eviction, `maxsize` configuration, and hit/miss tracking
- **medium** -- `@lru_cache` decorator or `LinkedHashMap` usage without explicit eviction monitoring
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

### Relationship To Other Concepts

- Related to [cache-aside](/concepts/cache-aside) because LRU is a common eviction policy for application-managed caches.
- Related to [read-through](/concepts/read-through) when bounded caches transparently load on misses and evict by recency.
- Related to [key-value-model](/concepts/key-value-model) because LRU caches are often implemented as bounded key-value stores with recency tracking.

### Boundary

Use `lru-cache` when cached entries are bounded and evicted by least-recently-used recency semantics.

Do not use it for any cache with size limits or TTL unless recency-based eviction is actually the defining behavior.
