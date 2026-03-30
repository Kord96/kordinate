---
description: Race Condition anti-pattern
type: anti-pattern
testable: true
graphable: false
---
# Race Condition

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Unsynchronized read-modify-write on shared mutable state (`count = count + 1` without a lock)
- Missing locks or mutexes around shared mutable data accessed by multiple threads or goroutines
- Check-then-act without atomicity (`if not exists(key): create(key)`)
- `if not exists then create` pattern without locking or compare-and-swap
- Concurrent map or dictionary access without a mutex or concurrent-safe data structure

### Confidence

- **high** -- shared mutable state is read and written by multiple threads/goroutines with no synchronization primitive in scope
- **medium** -- check-then-act pattern on shared resources without atomic operations or locks visible in the same function
- **low** -- global or module-level mutable variables accessed from functions that could plausibly be called concurrently

## Impact

Intermittent, hard-to-reproduce bugs that corrupt data and erode trust in the system.

### Symptoms

- Tests pass locally but fail intermittently in CI under parallel execution
- Data inconsistencies appear in production with no corresponding error logs
- Duplicate records created from concurrent requests that both passed a uniqueness check
- Counter values are lower than expected after concurrent increments
- Debugging is nearly impossible because the bug disappears under observation (Heisenbugs)

### Remediation

- Protect shared mutable state with a mutex, lock, or synchronized block appropriate to the language
- Use atomic operations (compare-and-swap, atomic increment) for simple counters and flags
- Replace check-then-act with atomic upsert operations (`INSERT ... ON CONFLICT`, `putIfAbsent`)
- Use concurrent-safe data structures (ConcurrentHashMap, sync.Map) instead of locking around standard collections
- Add race detector tools to CI (Go race detector, ThreadSanitizer) to catch races before production
