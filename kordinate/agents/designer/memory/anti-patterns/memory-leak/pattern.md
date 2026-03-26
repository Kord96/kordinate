---
description: Memory Leak anti-pattern
curated: true
scope: global
preloaded: none
---
# Memory Leak

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Event listeners never removed (`addEventListener` without corresponding `removeEventListener`)
- Growing dicts, lists, or caches in long-running processes without bounds or eviction
- Unclosed file handles, database connections, or network sockets (missing `close()`, `with`, or `using`)
- `__del__` relying on garbage collector timing for cleanup of external resources
- Circular references preventing garbage collection in reference-counted runtimes
- Global or module-level collections that accumulate entries over the process lifetime
- Timers or intervals (`setInterval`) that are never cleared

### Confidence

- **high** -- process RSS memory grows monotonically over hours/days under constant load, confirmed by heap dumps showing accumulation of specific object types
- **medium** -- event listeners are registered in a setup function but never deregistered, or a dict/list grows in a loop without bounds or TTL
- **low** -- resources are opened without a context manager or try-finally block, or `__del__` is used for cleanup of non-trivial resources

## Impact

OOM crashes in production, gradual performance degradation, and unpredictable restarts under sustained load.

### Symptoms

- Container or process memory usage grows steadily over time without recovering
- OOM kills appear in container orchestrator logs (Kubernetes OOMKilled)
- Garbage collection pauses become longer and more frequent
- Application response times degrade gradually after deployment until restart
- Heap dumps show unexpected retention of objects that should have been collected

### Remediation

- Use context managers (`with`, `using`, `try-finally`) for all resource acquisition to guarantee cleanup
- Remove event listeners in the corresponding teardown/unmount lifecycle (e.g., `useEffect` cleanup, `componentWillUnmount`)
- Bound all in-memory caches with a max size and TTL eviction policy (e.g., `functools.lru_cache`, `cachetools.TTLCache`)
- Profile memory in staging with tools like `tracemalloc`, Chrome DevTools heap snapshots, or `pprof` to detect leaks before production
- Avoid circular references or break them with `weakref` where the language runtime uses reference counting
