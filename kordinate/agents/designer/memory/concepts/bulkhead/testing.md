---
description: Bulkhead — testing guidance
curated: true
scope: global
preloaded: none
---
## Testing

Confirm that resource pools are truly isolated and that exhaustion of one pool does not affect others.

### Unit Tests

- Test pool isolation: exhaust one dependency's pool and assert that requests to other dependencies still succeed
- Verify rejection behavior: when a pool reaches its limit, assert new requests receive a fast-fail rejection, not queue indefinitely
- Test pool sizing: configure a pool with N slots, submit N+1 concurrent requests, and assert exactly one is rejected
- Assert per-pool metrics: active count, idle count, and rejected count are accurate after a burst of requests

### Integration Tests

- Run concurrent load against multiple real dependencies with separate bulkhead pools and verify no cross-contamination
- Test that a slow dependency saturates only its own pool while other dependency calls maintain normal latency
- Verify dynamic pool resizing if supported — change pool size at runtime and confirm new limits take effect

### Failure Injection

- Simulate a dependency that never responds and verify its pool fills to capacity while other pools remain healthy
- Inject a burst of requests exceeding all pool capacities simultaneously and confirm each pool rejects independently
- Kill a dependency mid-request for all in-flight pool slots and verify pool resources are reclaimed after timeout
