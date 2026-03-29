---
description: Cache-Aside — testing guidance
type: supplementary
---
## Testing

Verify the read-through and invalidation lifecycle: miss populates, hit returns cached, write invalidates.

### Unit Tests

- First read for a key misses cache, fetches from origin, and populates cache
- Second read for the same key returns cached data without hitting origin
- After a write/update, verify the cache entry is invalidated and the next read fetches fresh data

### Integration Tests

- Wire against real cache (Redis/Memcached) and origin database, verify full read-write-invalidate cycle
- Test TTL expiration: verify stale entries are evicted and subsequent reads re-fetch from origin

### Failure Injection

- Simulate cache unavailability and verify the application falls through to the origin database gracefully
