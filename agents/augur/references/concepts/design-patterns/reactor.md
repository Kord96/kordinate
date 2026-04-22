---
kind: concept
name: reactor
signatures: {}
source:
  memory_concept: memory/catalog/concepts/reactor.md
type: pattern
abstraction:
- concurrency
- architectural
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Single-threaded event loop dispatching I/O events to registered handlers
- Non-blocking I/O with callbacks, promises, or `async`/`await` syntax
- System calls: `select()`, `epoll()`, `kqueue()`, `IOCP`
- `asyncio.run()`, `loop.run_forever()`, event emitters, or `on('event', handler)`
- Libraries: Python `asyncio`/`twisted`, `libuv` (Node.js), Rust `tokio`/`mio`, Java NIO/Netty

### Confidence

- **high** -- Explicit event loop with `async def`/`await`, registered I/O handlers, and non-blocking socket operations
- **medium** -- Callback-based I/O handling without explicit loop management (Node.js default runtime model)
- **low** -- Any non-blocking I/O with event notification, even without a formal reactor abstraction

## Architecture

Look for a single-threaded event loop multiplexing I/O across many connections without blocking.

### Review Checklist

- No blocking calls inside the event loop (file I/O, DNS, CPU-heavy work offloaded to thread pool)
- Callback chains or async functions handle errors at each step, not just the top level
- Connection lifecycle is managed (timeouts, cleanup on disconnect)
- Backpressure is applied when write buffers fill up
- Graceful shutdown drains in-flight events before stopping the loop

### Anti-patterns

- Blocking the event loop with synchronous I/O or CPU-bound computation
- Deeply nested callback chains without error propagation (callback hell)
- Spawning a new event loop per request instead of multiplexing on one loop
- Ignoring backpressure -- writing faster than the socket can drain

### Relationship To Other Concepts

- Related to [event-driven](/concepts/event-driven) because reactor architectures dispatch work in response to readiness events and incoming signals.
- Related to [server-sent-events](/concepts/server-sent-events) when nonblocking event loops drive streaming IO.
- Related to [future-promise](/concepts/future-promise) because reactor-style systems often surface asynchronous completion through promise-like abstractions.

### Boundary

Use `reactor` when one event loop or readiness dispatcher multiplexes many IO sources and routes events to handlers without blocking threads per connection.

Do not use it for any async code. The key signal is readiness-based event loop architecture.
