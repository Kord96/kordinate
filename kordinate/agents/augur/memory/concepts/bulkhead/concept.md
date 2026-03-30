---
description: Bulkhead architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [resilience]
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
