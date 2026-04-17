---
description: Deadlock anti-pattern
type: anti-pattern
testable: true
observable: true
graphable: false
status: supporting
scope: cross-cutting
relationships:
  related_to:
  - distributed-lock
  - race-condition
  - read-write-lock
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Deadlock

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Multiple locks acquired in inconsistent order across different code paths
- Nested `synchronized` blocks, `with lock:` statements, or `mutex.Lock()` calls where inner locks vary by call site
- Circular wait on resources (thread A holds lock X and waits for lock Y, thread B holds lock Y and waits for lock X)
- Thread dumps showing BLOCKED threads waiting on each other in a cycle
- Database transactions that lock rows in different orders depending on the operation

### Confidence

- **high** -- thread dump or goroutine dump shows two or more threads blocked in a cycle, each holding a lock the other needs
- **medium** -- code acquires two or more locks in different orders across different functions or methods
- **low** -- nested lock acquisition exists but ordering appears consistent; risk increases if new call sites are added

## Impact

System hangs completely with no error message, requiring manual restart to recover.

### Symptoms

- Application stops responding but process is still alive and consuming no CPU
- Thread dumps show all worker threads in BLOCKED or WAITING state
- Health checks time out even though the process has not crashed
- The hang is intermittent and load-dependent, making reproduction difficult
- Restarting the service is the only recovery, causing downtime

### Remediation

- Establish and enforce a global lock ordering: always acquire locks in the same sequence everywhere
- Reduce lock scope to the minimum critical section needed, avoiding holding locks during I/O or external calls
- Use a single coarse lock instead of multiple fine-grained locks when the performance trade-off is acceptable
- Prefer lock-free data structures or channels/message passing over shared-state locking
- Add deadlock detection tooling (jstack analysis, Go deadlock detector, database lock wait monitoring) to CI and production alerting

### Relationship To Other Concepts

- Related to [distributed-lock](/concepts/distributed-lock) because poor lock lifecycle or acquisition ordering can deadlock distributed coordination too.
- Related to [race-condition](/concepts/race-condition) as another concurrency failure mode, though deadlock is about circular waiting rather than unsynchronized interleaving.
- Related to [read-write-lock](/concepts/read-write-lock) when lock hierarchies or upgrade paths create waiting cycles.

### Boundary

Use `deadlock` when progress halts because actors each hold resources the others need, forming a circular wait.

Do not use it for generic slowness, starvation, or one-way blocking without a real wait cycle.
