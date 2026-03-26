---
description: Bulkhead architectural pattern
curated: true
scope: global
preloaded: none
---
# Bulkhead


## Recognition

How to identify this pattern in code.

### Signatures

- `resilience4j-bulkhead` dependency and `@Bulkhead` annotations (Java)
- Hystrix thread pool isolation configuration (`HystrixCommand` with `threadPoolKey`)
- Envoy circuit breaking configuration with `max_connections`, `max_pending_requests` per cluster
- `Semaphore`-based isolation limiting concurrent access to a resource
- `ThreadPoolBulkhead` configuration in Java resilience libraries
- Separate thread pools or connection pools allocated per downstream dependency

### Confidence

- **high** -- named bulkhead instances per dependency with explicit pool sizing, rejection metrics, and fallback behavior
- **medium** -- separate connection pools or thread pools per dependency but without formal bulkhead library usage or rejection handling
- **low** -- single pool with per-dependency concurrency limits enforced via semaphores or ad-hoc locking

## Architecture

Look for isolated resource pools per dependency — one failing dependency must not exhaust all resources.

### Review Checklist

- Each external dependency has its own bounded resource pool (threads, connections)
- Pool sizes are configured per dependency based on expected load
- Pool exhaustion triggers rejection (fast fail), not unbounded queuing
- Metrics exposed per pool: active, idle, waiting, rejected counts

### Anti-patterns

- Single shared connection/thread pool across all dependencies
- No pool size limits — one slow dependency consumes all available resources
- Bulkhead without monitoring — pool exhaustion goes unnoticed until outage

## Monitoring

Track per-pool utilization and rejection rates to detect resource exhaustion before it cascades.

### Key Metrics

- `bulkhead_pool_active` (gauge) — currently active slots per pool
- `bulkhead_pool_available` (gauge) — remaining capacity per pool
- `bulkhead_rejections_total` (counter) — requests rejected due to pool exhaustion
- `bulkhead_wait_duration_seconds` (histogram) — time spent waiting for a pool slot

### Alerts

- Pool utilization consistently above 80% (approaching exhaustion)
- Rejection rate exceeding threshold for any single pool
- Wait duration p99 exceeding acceptable latency (pool undersized)
- Multiple pools exhausting simultaneously (systemic resource pressure)

## Deployment

Pool size changes and connection draining must be coordinated to avoid resource exhaustion during rollout.

### Rollout Implications

- Reducing pool sizes during rollout can cause immediate rejection spikes if in-flight requests exceed the new limit
- New pods starting with fresh pools must warm up connections — expect higher latency during the initial requests
- Rolling restart temporarily reduces total pool capacity across the fleet — size pools to handle full load with one fewer pod
- Connection draining must complete before pod termination — active connections in a pool that are forcibly closed cause client errors

### Pre-deploy Checklist

- Verify pool size changes are gradual (not halving capacity in one step) to avoid rejection spikes
- Confirm terminationGracePeriodSeconds allows full connection draining per pool
- Check that monitoring is in place for per-pool rejection rates during the rollout window

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
