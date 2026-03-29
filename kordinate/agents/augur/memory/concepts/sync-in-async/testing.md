---
description: Sync-in-Async — testing guidance
type: supplementary
---
# Testing

- Lint for blocking calls inside `async def` functions: `requests.*`, `time.sleep()`, `open()`, `subprocess.run()`
- Test that async handlers do not block the event loop by running concurrent requests and measuring throughput
- Verify that async HTTP clients (`httpx.AsyncClient`, `aiohttp`) are used instead of synchronous `requests`
- Test event loop warnings: enable asyncio debug mode and assert no "took X seconds" slow callback warnings
- Assert that all database drivers in async code are async-native (`asyncpg`, `motor`, not `psycopg2`)
- Test that unavoidable blocking calls are wrapped in `asyncio.to_thread()` or `run_in_executor()`
- Benchmark async endpoint throughput under concurrent load to verify it scales as expected
