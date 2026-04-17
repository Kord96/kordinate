---
description: Object Pool architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- design
- infrastructure
status: primary
scope: backend
relationships:
  related_to:
  - connection-pooling
  - worker-pool
  - flyweight
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Object Pool

## Recognition

How to identify this pattern in code.

### Signatures

- Methods named `acquire()`, `release()`, `borrow()`, `return_to_pool()`, `get()`, `put()`
- Pool size configuration: `max_size`, `min_idle`, `max_idle`, `pool_size`
- Connection pool classes: `ConnectionPool`, `ThreadPool`, `WorkerPool`
- Python: `asyncio.Queue` used as a pool, `multiprocessing.Pool`, `concurrent.futures.*Executor`
- Java: `ExecutorService`, `HikariCP`, `Commons Pool`
- Go: `sync.Pool`, buffered channels used as pools

### Confidence

- **high** -- class with `acquire()`/`release()` pair, pool size limits, and resource reuse tracking
- **medium** -- connection pool library configuration (HikariCP, pgBouncer, `asyncpg.create_pool`)
- **low** -- pre-allocated array of objects with index-based checkout

## Architecture

Look for correct lifecycle management: acquire, use, release, and handling of stale or broken resources.

### Review Checklist

- Resources are always returned to the pool (try/finally or context manager)
- Pool handles stale or broken resources (validation on acquire, eviction on error)
- Maximum pool size prevents unbounded resource consumption
- Timeout on acquire prevents indefinite blocking when pool is exhausted
- Pool shutdown drains and closes all resources cleanly

### Anti-patterns

- Acquired resources not returned on error paths (resource leak)
- No health check on pooled objects -- stale connections handed to callers
- Unbounded pool growth (no max size) defeating the purpose of pooling
- Pool used for cheap-to-create objects where allocation is faster than pool overhead

### Relationship To Other Concepts

- Related to [connection-pooling](/concepts/connection-pooling) because pooled network or database connections are one specialized object-pool form.
- Related to [worker-pool](/concepts/worker-pool) because both manage bounded reusable resources, though worker pools schedule active executors rather than passive instances.
- Related to [flyweight](/concepts/flyweight) because both reduce allocation pressure, though object pools reuse full objects over time while flyweights share intrinsic state.

### Boundary

Use `object-pool` when expensive objects are checked out, reused, and returned from a bounded pool.

Do not use it for simple caches, immutable shared state, or one-shot resource factories.
