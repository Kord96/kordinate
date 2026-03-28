## Testing

Verify that concurrent cache misses for the same key produce exactly one origin fetch.

### Unit Tests

- Expire a cache key and send N concurrent requests — assert only one origin fetch occurs
- Verify all N waiters receive the same recomputed value once the single fetch completes
- Test lock timeout: if the recomputing request hangs, waiters eventually fall through or receive an error

### Integration Tests

- Wire against real cache and origin, expire a hot key, and verify origin query count equals 1 under load
- Test probabilistic early recompute (XFetch): verify refresh happens before TTL, avoiding any stampede window

### Failure Injection

- Kill the holder of the recompute lock mid-fetch and verify waiters recover rather than deadlock

## Monitoring

Track lock contention, origin load during recomputation, and coalesced request counts.

### Key Metrics

- `cache_recompute_total` (counter) — actual origin fetches (should be 1 per expired key, not N)
- `cache_coalesced_requests_total` (counter) — requests that waited on another's recomputation
- `cache_lock_wait_seconds` (histogram) — time waiters spend blocked on the recompute lock
- `cache_early_recompute_total` (counter) — probabilistic early refreshes (if using XFetch)

### Alerts

- Multiple concurrent recomputes for the same key (stampede prevention failure)
- Lock wait time exceeding acceptable latency threshold
- Origin load spike correlating with cache expiration events

