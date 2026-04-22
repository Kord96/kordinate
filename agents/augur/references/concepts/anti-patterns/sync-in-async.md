---
kind: concept
name: sync-in-async
signatures: {}
source:
  memory_concept: memory/catalog/concepts/sync-in-async.md
type: anti-pattern
abstraction: []
scope: backend
status: supporting
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `requests.get()` or `requests.post()` inside an `async def` function
- Blocking I/O (`open()`, `socket.recv()`, `subprocess.run()`) in asyncio coroutines
- `time.sleep()` in an async function (should be `await asyncio.sleep()`)
- `open()` for file I/O without `aiofiles` in async code
- Database drivers without async support (`psycopg2` instead of `asyncpg`) used in async handlers
- `os.path.exists()`, `os.listdir()`, or other blocking OS calls in coroutines
- `urllib.request.urlopen()` inside `async def`
- Synchronous ORM calls (Django ORM without `sync_to_async`) in async views

### Confidence

- **high** -- `requests.get()` or `time.sleep()` directly inside an `async def`, especially in a web handler (FastAPI, aiohttp)
- **medium** -- blocking file I/O or synchronous database calls inside async functions, but wrapped in `run_in_executor`
- **low** -- synchronous utility calls in async code where the blocking duration is very short (< 1ms)

## Impact

Blocks the event loop, defeating the concurrency benefits of async and causing all concurrent tasks to stall.

### Symptoms

- Async web server handles requests sequentially despite async framework
- Response latency spikes when any single request involves blocking I/O
- Event loop warnings: `asyncio` reports "Executing ... took X seconds"
- Throughput does not improve with concurrent requests as expected from async architecture
- CPU usage is low while the event loop is blocked on I/O waits

### Remediation

- Replace `requests` with `httpx.AsyncClient` or `aiohttp.ClientSession` for HTTP calls
- Replace `time.sleep()` with `await asyncio.sleep()`
- Use `aiofiles` for file operations in async code
- Use async database drivers (`asyncpg`, `motor`, `aiosqlite`) instead of synchronous ones
- Wrap unavoidable blocking calls in `asyncio.to_thread()` or `loop.run_in_executor()`

### Relationship To Other Concepts

- Related to [future-promise](/concepts/future-promise) because blocking on futures inside async flows is a common sync-in-async failure mode.
- Related to [busy-waiting](/concepts/busy-waiting) when sync waits are emulated by polling loops inside asynchronous code.
- Related to [reactor](/concepts/reactor) because blocking operations inside event-loop systems undermine the whole readiness-driven model.

### Boundary

Use `sync-in-async` when blocking synchronous work or waits are performed inside an asynchronous execution context, stalling concurrency.

Do not use it for async wrappers around unavoidable CPU work that is intentionally isolated onto worker threads or executors.
