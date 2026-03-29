---
description: Distributed Lock — testing guidance
type: supplementary
---
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
