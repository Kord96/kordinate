---
description: LRU Cache — testing guidance
type: supplementary
---
## Testing

Verify eviction order, cache correctness, and behavior under capacity and concurrency.

### Unit Tests

- Fill the cache to capacity, add one more entry, and assert the least-recently-used entry was evicted
- Access an entry to make it recently used, then fill the cache, and verify it survives eviction
- Verify cache keys are deterministic: equivalent inputs produce cache hits, not duplicate entries

### Concurrency Tests

- Access the cache from multiple threads simultaneously and verify no corrupted entries or lost updates
- Verify that concurrent reads and writes do not deadlock

### Edge Cases

- Test cache with `maxsize=1` and verify correct single-entry behavior
- Cache a mutable object, modify it externally, and verify the cache returns the original (defensive copy check)
- Verify TTL-based invalidation: entries expire after the configured duration
