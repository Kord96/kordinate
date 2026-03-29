---
description: Deadlock — testing guidance
type: supplementary
---
## Testing

Reproduce lock-ordering violations under controlled concurrency to verify prevention and detection mechanisms.

### Unit Tests

- Verify that lock acquisition follows a consistent global ordering — assert that acquiring locks out of order raises an error or is prevented
- Test lock timeout behavior: a thread unable to acquire a lock within the timeout should receive an explicit error, not hang
- Assert that lock-free or optimistic alternatives correctly detect conflicts and retry

### Concurrency Tests

- Spawn two threads that acquire the same two locks in opposite order and verify the deadlock detector triggers or the ordering constraint prevents it
- Stress-test critical sections with high concurrency to surface contention hotspots
- Verify that database-level deadlock detection returns a retryable error and the application retries successfully

### Static Analysis

- Use lock-order analysis tools or thread-safety annotations to catch potential deadlocks at build time rather than runtime
