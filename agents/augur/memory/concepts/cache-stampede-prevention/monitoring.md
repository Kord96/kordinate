---
description: Cache Stampede Prevention — monitoring guidance
type: supplementary
---
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
