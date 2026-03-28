---
description: Reactor/Event Loop architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [concurrency, architectural]
---
# Reactor/Event Loop

## Recognition

How to identify this pattern in code.

### Signatures

- Single-threaded event loop dispatching I/O events to registered handlers
- Non-blocking I/O with callbacks, promises, or `async`/`await` syntax
- System calls: `select()`, `epoll()`, `kqueue()`, `IOCP`
- `asyncio.run()`, `loop.run_forever()`, event emitters, or `on('event', handler)`
- Libraries: Python `asyncio`/`twisted`, `libuv` (Node.js), Rust `tokio`/`mio`, Java NIO/Netty
- Java: Netty `EventLoopGroup`, `NioEventLoopGroup`, `Channel`, `ChannelHandler` with event-driven I/O
- Java: NIO `Selector`, `SelectionKey`, `SocketChannel` for multiplexed non-blocking I/O
- Java: Vert.x `Vertx`, `EventBus`, `Verticle` with event loop model

### Negative signals (not reactor pattern)

- Java: Using Project Reactor (`Mono`, `Flux`) or Spring WebFlux is reactive programming, NOT the reactor/event loop pattern
- Reactive Streams API usage (`Publisher`, `Subscriber`) is a different concept (reactive programming, not the reactor pattern)
- Only flag reactor when there is an actual event loop multiplexing I/O, not just reactive type usage
- Python: Simply using `asyncio` / `async def` / `await` in application code is NOT the reactor pattern -- it is merely using the language's async runtime. The reactor pattern is present only when the codebase **implements or configures** the event loop itself (e.g., custom EventLoopPolicy, `loop.run_forever()`, `select()`-based I/O multiplexing). A task queue or web framework that uses `async def` is just async, not reactor
- TypeScript/Node.js: Using `async/await` or Promises in application code is NOT the reactor pattern. Node.js itself uses the reactor pattern internally (libuv), but application code sitting on top of it does not constitute implementing the pattern
- The presence of `EventLoop` or `event_loop` in variable names used to obtain or pass the running asyncio loop is not evidence of the reactor pattern

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
