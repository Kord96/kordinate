---
description: Leader Election — testing guidance
type: supplementary
---
## Testing

Verify correct election, fencing, and failover behavior under normal and partitioned conditions.

### Unit Tests

- Start multiple candidates and assert exactly one wins the election
- Verify that the leader renews its lease and followers do not attempt to take over while the lease is valid
- Assert that fencing tokens or epoch numbers increment on each new election

### Integration Tests

- Kill the leader process and verify a follower wins the new election within the expected TTL window
- Simulate a network partition between leader and the coordination store and confirm the leader steps down after lease expiry
- Restore the partition and verify the old leader does not reclaim leadership using a stale fencing token

### Failure Injection

- Introduce clock skew between nodes and verify the election protocol still produces a single leader
- Simulate a slow leader that cannot renew its lease in time and confirm followers take over cleanly
