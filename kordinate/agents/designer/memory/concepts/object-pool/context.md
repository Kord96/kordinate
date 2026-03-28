## Testing

Test resource lifecycle management, pool bounds enforcement, and behavior under contention.

### Unit Tests

- Acquire a resource, verify it is valid, release it, acquire again, and verify the same instance is reused
- Exhaust the pool to max_size and verify the next acquire blocks or times out as configured
- Release a broken resource and verify the pool evicts it rather than handing it to the next caller
- Verify pool shutdown closes all resources, including those currently checked out

### Concurrency Tests

- Acquire and release from multiple threads simultaneously and verify no resource is handed to two callers at once
- Stress-test with more concurrent acquirers than pool capacity to verify correct blocking and fairness
- Verify no resource leak when an acquirer thread is interrupted or times out

### Integration Tests

- Wire the pool with real resources (database connections, HTTP clients) and verify health-check-on-acquire catches stale objects
- Simulate a backend restart and verify the pool recovers by evicting dead connections and creating fresh ones
- Confirm pool metrics (active count, idle count, wait time) report accurately under load

