---
description: Distributed Lock architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [concurrency, resilience]
---
# Distributed Lock

## Recognition

How to identify this pattern in code.

### Signatures

- Lock acquire/release calls with TTL (time-to-live) for automatic expiry
- Redis-based locking: `SETNX`, `SET NX EX`, Redlock algorithm across multiple Redis instances
- etcd lock operations using `concurrency.NewMutex`
- Database advisory locks (`pg_advisory_lock`, `GET_LOCK` in MySQL)
- Optimistic locking with version fields (`version`, `etag`, compare-and-swap)
- Lock key naming conventions: `lock:resource:id`, `distributed-lock-*`
- Try-lock patterns with timeout and retry logic

### Negative signals (not sufficient for detection)

- Go `sync.Mutex` and `sync.RWMutex` are in-process locks, NOT distributed locks. The pattern requires a shared lock store (Redis, etcd, database) accessible across multiple processes or nodes.
- Java `synchronized`, `ReentrantLock`, `ReentrantReadWriteLock` are in-process locks, not distributed locks.
- File locks (`flock`, `lockfile`) are OS-level locks, not distributed locks (unless used on a shared filesystem like NFS).
- The word `Mutex` alone in Go is standard concurrency, not distributed locking. Look for Redis `SETNX`, etcd `concurrency`, or database advisory lock calls.

### Confidence

- **high** -- explicit distributed lock implementation with TTL, acquire/release semantics, and a shared lock store (Redis, etcd, DB)
- **medium** -- database row-level locking or optimistic concurrency control with version fields
- **low** -- in-process mutex used in a multi-instance deployment (broken distributed locking)

## Architecture

Look for correct lock lifecycle management with TTL, fencing, and proper handling of lock loss during execution.

### Review Checklist

- Lock TTL is set appropriately (long enough for the operation, short enough for timely recovery)
- Lock holder checks ownership before releasing (does not release a lock it no longer holds)
- Fencing tokens are used to prevent operations from completing after lock expiry
- Lock acquisition has a bounded timeout (does not block indefinitely)
- Graceful handling when lock is lost mid-operation (operation is idempotent or compensatable)

### Anti-patterns

- No TTL on locks (risk of permanent deadlock if the holder crashes)
- Releasing a lock without verifying ownership (may release another process's lock)
- Using in-process locks (mutex/semaphore) in a distributed multi-instance deployment
- Redlock without sufficient independent Redis instances (minimum 5 for safety guarantees)
