---
description: Read-Through Cache — testing guidance
type: supplementary
---
## Testing

Verify transparent load-on-miss behavior, correct TTL eviction, and graceful handling of loader failures.

### Unit Tests

- Request a key not in cache, verify the loader is called, and the value is returned and cached
- Request the same key again and verify the loader is not called (cache hit)
- Wait for TTL expiry, request the key, and verify the loader is called again (stale eviction)
- Verify the loader is called with the correct key and parameters

### Failure Handling Tests

- Simulate a loader failure and verify the cache does not cache the error (no negative caching of exceptions)
- Verify a failed load for one key does not affect cached values for other keys
- Test bulk loading: request multiple keys in a batch and verify the loader is called once for all missing keys

### Concurrency Tests

- Request the same uncached key from multiple threads simultaneously and verify the loader is called only once (stampede protection)
- Verify concurrent reads of cached keys do not block each other
- Test cache warming on startup: verify pre-populated keys are served from cache without loader calls
