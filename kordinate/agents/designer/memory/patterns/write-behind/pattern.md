---
description: Write-Behind architectural pattern
curated: true
scope: global
preloaded: none
---
# Write-Behind

## Recognition

How to identify this pattern in code.

### Signatures

- Writes go to cache first, then asynchronously flushed to the backing store
- Write-through variant: synchronous write to both cache and store
- Cache warming or preloading on startup
- Write coalescing: multiple writes to the same key batched into a single store write
- Async flush workers, write buffers, or dirty-flag tracking on cached entries
- Configuration for flush intervals, batch sizes, or write-behind delay
- Libraries: Hazelcast write-behind, Redis with async persistence, NCache

### Confidence

- **high** -- writes target cache with explicit async flush to backing store and coalescing logic
- **medium** -- write-through with synchronous dual-write to cache and database
- **low** -- application writes to an in-memory buffer that periodically syncs to storage

## Architecture

Look for cache as the primary write target with deferred or synchronous propagation to the persistent store.

### Review Checklist

- Data durability guarantees are documented (what happens if cache crashes before flush)
- Flush failures are retried with backoff and dead-letter handling
- Write ordering is preserved when coalescing (last-write-wins or merge strategy is explicit)
- Cache and backing store consistency is monitored (drift detection)
- Startup handles cache warming from the backing store before accepting writes

### Anti-patterns

- No durability guarantee: cache is sole copy and data is lost on crash
- Unbounded write-behind buffer that grows until memory is exhausted
- Flush errors silently dropped, leading to permanent data loss
- Write-behind delay so long that reads from the backing store return stale data
