## Testing

Verify concurrent reader access, exclusive writer access, and absence of deadlock or starvation.

### Unit Tests

- Acquire a read lock from two threads simultaneously and verify both succeed (shared access)
- Acquire a write lock and verify a concurrent read lock acquisition blocks until the write lock is released
- Acquire a read lock and verify a concurrent write lock acquisition blocks until all read locks are released
- Test lock timeout: attempt to acquire a write lock while readers hold it, and verify timeout fires correctly

### Starvation Tests

- Run continuous readers and verify a waiting writer eventually acquires the lock (no write starvation)
- Run a long-running writer and verify waiting readers are served promptly after the write lock is released
- Verify lock fairness: writers waiting before readers are served first (if the implementation guarantees fairness)

### Deadlock Tests

- Attempt to upgrade a read lock to a write lock and verify the behavior matches the contract (atomic upgrade or explicit error)
- Acquire locks in nested order from multiple threads and verify no deadlock occurs with consistent ordering
- Verify lock acquisition with timeout prevents indefinite blocking in all contention scenarios

