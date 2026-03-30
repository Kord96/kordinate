---
description: Worker/Thread Pool architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [concurrency, infrastructure]
---
# Worker/Thread Pool

## Recognition

How to identify this pattern in code.

### Signatures

- Fixed pool of workers processing tasks submitted to a shared queue
- `ThreadPoolExecutor`, `ProcessPoolExecutor`, or equivalent pool constructors
- Worker count configuration (often tied to CPU count or a config value)
- `submit()`, `map()`, or `apply_async()` calls dispatching work to the pool
- Libraries: Python `concurrent.futures`, Go goroutine pools, Node `worker_threads`, Java `ExecutorService`

### Confidence

- **high** -- Explicit pool instantiation with `ThreadPoolExecutor(max_workers=N)` or equivalent
- **medium** -- Fixed number of goroutines or threads pulling from a shared channel/queue
- **low** -- Multiple workers processing tasks concurrently without a formal pool abstraction

## Architecture

Look for a fixed set of reusable workers pulling tasks from a shared submission queue.

### Review Checklist

- Pool size is configurable and documented (not hardcoded magic numbers)
- Tasks submitted to the pool are independent -- no hidden shared state between tasks
- Pool shutdown is graceful: pending tasks complete before termination
- Exceptions in worker tasks are captured and reported, not silently lost
- Resource limits are enforced (max queue depth, task timeout)
- Future/result objects are consumed -- no fire-and-forget leaks

### Anti-patterns

- Creating a new thread per task instead of reusing pooled workers
- Pool size equal to unbounded input (defeats the purpose of pooling)
- Blocking the main thread waiting on every future immediately after submission (serial execution)
- No timeout on task execution, allowing hung tasks to consume a worker forever
