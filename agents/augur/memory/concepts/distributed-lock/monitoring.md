---
description: Distributed Lock — monitoring guidance
type: supplementary
---
## Monitoring

Track lock acquisition, contention, and expiry to detect coordination failures across nodes.

### Key Metrics

- `distributed_lock_held_duration_seconds` (histogram) — how long locks are held before release
- `distributed_lock_acquisition_total` (counter) — successful lock acquisitions, by resource
- `distributed_lock_contention_total` (counter) — failed acquisition attempts due to an existing holder
- `distributed_lock_expired_total` (counter) — locks that expired before explicit release (potential split-brain)

### Alerts

- Lock held longer than the expected TTL (holder may be stuck or partitioned)
- Rising lock expiry rate (nodes are losing locks before completing work)
- High contention ratio on a single resource (bottleneck or hot key)
