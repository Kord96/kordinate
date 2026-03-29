---
description: Connection Pooling — testing guidance
type: supplementary
---
## Testing

Verify pool lifecycle, bounded concurrency, and correct connection reuse behavior.

### Unit Tests

- Acquire and release a connection — verify it returns to the pool for reuse
- Acquire connections up to the max pool size and verify the next request waits or times out
- Test idle eviction: leave a connection idle beyond the TTL and verify it is closed and replaced

### Integration Tests

- Run concurrent workloads through the pool against a real database and verify no connection leaks
- Test pool warm-up: verify minimum connections are established at startup

### Failure Injection

- Kill the database server and verify the pool detects dead connections, evicts them, and reconnects when the server recovers
