---
description: Object Pool architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design, infrastructure]
---
# Object Pool

## Recognition

How to identify this pattern in code.

### Signatures

- Methods named `acquire()`, `release()`, `borrow()`, `return_to_pool()`, `get()`, `put()`
- Pool size configuration: `max_size`, `min_idle`, `max_idle`, `pool_size`
- Connection pool classes: `ConnectionPool`, `ThreadPool`, `WorkerPool`
- Python: `asyncio.Queue` used as a pool, `multiprocessing.Pool`, `concurrent.futures.*Executor`
- Java: `ExecutorService`, `HikariCP`, `Commons Pool` (`GenericObjectPool`, `PooledObjectFactory`)
- Java: `io.netty.buffer.PooledByteBufAllocator`, `io.netty.channel.pool.ChannelPool`
- Java: custom pool with `ConcurrentLinkedQueue` or `BlockingQueue` as backing store with create/destroy lifecycle
- Go: `sync.Pool`, buffered channels used as pools
- TypeScript: keyed client pool (`WebClientPool`, `ClientPool`) that caches and reuses client instances by token or key instead of creating new ones per request
- Python: `Resource` base class with `acquire()`/`release()` methods used by `ConnectionPool`, `ChannelPool`, `ProducerPool` (e.g., Kombu's `kombu.resource.Resource`)
- Generic resource pool: class wrapping a queue/map of reusable objects with size limits, providing `get`/`put` or `acquire`/`release` semantics

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
