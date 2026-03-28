## Testing

Verify mutual exclusion guarantees hold under concurrent access and that lock expiry prevents indefinite blocking.

### Unit Tests

- Acquire a lock and assert a second attempt on the same resource fails or blocks
- Verify lock release allows the next waiter to acquire immediately
- Test TTL expiry: hold a lock without releasing it and confirm it becomes available after the TTL elapses
- Assert that fencing tokens increment monotonically and stale tokens are rejected by the protected resource

### Integration Tests

- Run two processes competing for the same lock and verify only one enters the critical section at a time
- Simulate a lock holder crash (kill the process) and verify the lock is eventually released via TTL
- Test lock renewal/heartbeat: a long-running holder that renews should not lose its lock to expiry

### Partition Tests

- Simulate a network partition between the lock holder and the lock backend — verify the holder stops assuming it holds the lock after failing to renew
- Test split-brain scenarios: both sides of a partition believe they hold the lock — fencing tokens should prevent conflicting writes

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

## Deployment

Coordinate rollouts carefully since lock semantics depend on consistent behavior across all nodes.

### Rollout Implications

- Rolling updates mean old and new code may compete for the same locks — ensure lock key naming and TTL semantics are unchanged or backward-compatible
- If changing lock TTL, deploy the increase first; a decreased TTL on new nodes while old nodes hold longer locks can cause premature expiry assumptions
- Verify the lock backend (Redis, ZooKeeper, etcd) is healthy before starting the rollout — degraded coordination makes lock behavior unpredictable
- Drain work from nodes before termination to avoid locks being held by dying processes

### Pre-deploy Checklist

- Confirm lock backend quorum is intact and latency is within normal bounds
- Verify fencing tokens or lock versioning is in place to prevent stale lock holders from making writes

