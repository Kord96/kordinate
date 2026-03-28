---
description: Worker/Thread Pool architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
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
- Go: fixed number of goroutines started in a loop (`for i := 0; i < numWorkers; i++ { go worker(jobs) }`) reading from a shared channel
- Go: `errgroup.Group` with `SetLimit(n)` for bounded concurrent work
- Go: `semaphore.NewWeighted(n)` controlling concurrent goroutine count
- Go: `gammazero/workerpool` or `panjf2000/ants` pool libraries
- Go: `numWorkers` or `maxWorkers` config fields with goroutine spawning loops
- Java: `Executors.newFixedThreadPool(n)`, `Executors.newCachedThreadPool()`, `ForkJoinPool`
- Java: `@Async` with custom `TaskExecutor` bean configuration
- Java: Spring `ThreadPoolTaskExecutor` with `setCorePoolSize()` / `setMaxPoolSize()` configuration
- Any: class/struct named `WorkerPool`, `Pool`, or `Workers` managing a fixed set of processing goroutines/threads

### Negative signals (not sufficient for detection)

- Go: a single `go func()` goroutine is not a worker pool -- look for a fixed count of goroutines processing from a shared channel
- Go: `sync.WaitGroup` alone is synchronization, not a pool (unless paired with a fixed number of goroutines)
- Python: importing `concurrent.futures` or `multiprocessing.Pool` in test code for parallel test execution is test infrastructure, not the worker-pool architectural pattern. Only flag when the application itself uses a pool for processing work
- Python: `ThreadPoolExecutor` used by a web framework (e.g., `starlette`, `uvicorn`) internally is framework plumbing, not an architectural choice by the project

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
