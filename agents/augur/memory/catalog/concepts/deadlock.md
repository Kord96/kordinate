---
description: Deadlock anti-pattern
type: anti-pattern
testable: true
observable: true
graphable: false
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
