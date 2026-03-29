---
description: Race Condition — testing guidance
type: supplementary
---
## Testing

Detect and verify fixes for race conditions using concurrency stress tests, race detectors, and deterministic scheduling.

### Static Analysis

- Enable race detector in CI (Go `-race` flag, ThreadSanitizer for C/C++/Rust) and run the full test suite
- Scan for unsynchronized read-modify-write patterns on shared mutable state
- Check for check-then-act sequences without atomicity (TOCTOU bugs)

### Concurrency Tests

- Run the suspected racy operation from multiple threads/goroutines simultaneously and verify the outcome is consistent
- Increment a shared counter from N threads and verify the final value equals N (detects missing synchronization)
- Execute the check-then-act path concurrently and verify no duplicate records or double-execution

### Deterministic Reproduction

- Use controlled scheduling (thread barriers, latches) to force the exact interleaving that triggers the race
- Inject a delay between the check and the act to widen the race window and make it reproducible
- After fixing, re-run the stress test to confirm the fix holds under contention

### Regression

- Add the failing concurrent test case to CI as a permanent regression test
- Document the race scenario (which threads, which shared state, which interleaving) in the test for future maintainers
