---
description: Unbounded Growth anti-pattern
type: anti-pattern
observable: true
curated: true
scope: global
preloaded: none
---
# Unbounded Growth

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Lists or dicts that grow without bound (`cache = {}` with no eviction)
- No TTL on cache entries (items added but never expired)
- No max size on collections (no `maxlen`, `maxsize`, or capacity check)
- Append-only patterns without eviction (`history.append()` in a long-running process)
- `@lru_cache` without `maxsize` parameter (defaults to 128, but `maxsize=None` means unbounded)
- In-memory queues with no consumer backpressure or size limit
- Log buffers or event collectors that accumulate indefinitely
- Session stores or connection pools that grow but never shrink

### Confidence

- **high** -- a dict or list in a long-running process grows monotonically with no eviction, TTL, or size limit, and memory usage climbs over time
- **medium** -- cache or collection has no visible size limit, but the growth rate may be slow enough to not trigger OOM quickly
- **low** -- `append()` or dict assignment in a loop without clear bounds, but the process may be short-lived

## Impact

Memory exhaustion and OOM crashes in long-running processes as collections grow without limit.

### Symptoms

- Application memory usage increases steadily over hours or days
- OOM kills in production after extended uptime (visible in `dmesg` or container logs)
- Performance degrades gradually as data structures grow (slower lookups, GC pressure)
- Restarting the process temporarily resolves memory issues
- Memory profiling shows a single dict or list consuming most of the heap

### Remediation

- Use `collections.OrderedDict` with size-limited eviction or `functools.lru_cache(maxsize=N)`
- Set TTL on cache entries using `cachetools.TTLCache` or equivalent
- Use `collections.deque(maxlen=N)` instead of unbounded lists for rolling buffers
- Implement backpressure or size limits on in-memory queues
- Add memory monitoring and alerts for long-running processes to catch growth before OOM
