---
kind: concept
name: read-write-lock
signatures: {}
source:
  memory_concept: memory/catalog/concepts/read-write-lock.md
type: pattern
abstraction:
- concurrency
scope: backend
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Separate lock acquisition for read vs write operations
- Multiple concurrent readers allowed, exclusive access for writers
- `RLock`, `RWMutex`, `ReadWriteLock`, `shared_lock`/`unique_lock`
- `acquire_read()`/`acquire_write()` or `r_lock()`/`w_lock()` method pairs
- Libraries: Go `sync.RWMutex`, Java `ReentrantReadWriteLock`, Rust `std::sync::RwLock`, C++ `std::shared_mutex`
- Python has no stdlib RWLock; use `readerwriterlock` package or custom implementation

### Confidence

- **high** -- Explicit `RWMutex` or `ReadWriteLock` with distinct read/write acquisition paths
- **medium** -- Custom lock implementation distinguishing between shared and exclusive access
- **low** -- Any locking scheme where reads are treated differently from writes, even with a regular mutex

## Architecture

Look for shared resources protected by a lock that permits concurrent reads but serializes writes.

### Review Checklist

- Write starvation is addressed (writers eventually acquire the lock even under heavy read load)
- Lock scope is minimal -- held only for the duration of the critical section
- Upgrade from read lock to write lock is either atomic or explicitly disallowed (no deadlock risk)
- Lock acquisition has a timeout to prevent indefinite blocking

### Anti-patterns

- Using a read-write lock where a simple mutex would suffice (premature optimization)
- Holding the write lock during I/O or network calls (long lock hold times starve readers)
- Nested lock acquisition without consistent ordering (deadlock risk)
- Read lock acquired but the code path mutates shared state

### Relationship To Other Concepts

- Related to [race-condition](/concepts/race-condition) because read-write locks are one way to protect shared state against unsafe concurrent access.
- Related to [deadlock](/concepts/deadlock) because lock upgrade paths and nested ordering mistakes can create waiting cycles.
- Related to [optimistic-locking](/concepts/optimistic-locking) as a contrasting concurrency strategy that avoids long-held shared locks.

### Boundary

Use `read-write-lock` when a shared resource allows concurrent readers but requires exclusive writers through an explicit RW lock primitive.

Do not use it for any mutex or any code that merely reads more often than it writes.
