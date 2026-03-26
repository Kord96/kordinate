---
description: Sync-in-Async anti-pattern
type: anti-pattern
testable: true
curated: true
scope: global
preloaded: none
---
# Sync-in-Async

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
