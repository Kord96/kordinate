---
description: Future/Promise architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [concurrency, design]
---
# Future/Promise

## Recognition

How to identify this pattern in code.

### Signatures

- Custom deferred computation types: `Deferred`, `DeferredPromise`, `CompletableFuture`, `SettablePromise`
- Manual promise construction: `new Promise((resolve, reject) =>` with deferred resolution
- Composition primitives as architectural pattern: `Promise.allSettled()`, `Promise.race()`, `asyncio.gather()`, `CompletableFuture.thenCompose()`
- Cancellation support: `AbortController` integration, `CancelToken`, cancellable promise wrappers
- Libraries: Python `concurrent.futures`, Java `CompletableFuture`, Rust `Future` trait, Go channels used as futures

**Not this pattern:** Standard `async/await` or `.then()` usage is baseline language syntax in JS/TS/Python, not the future/promise architectural pattern. Only flag when the codebase builds custom deferred types, implements cancellation, or uses futures as a concurrency coordination primitive (e.g., `Promise.race` for timeouts, custom `Deferred` class).

### Confidence

- **high** -- Custom `Deferred`/`Future` class with manual resolve/reject, or `CompletableFuture` composition chains
- **medium** -- `Promise.race`/`Promise.allSettled` used as architectural coordination (timeout patterns, parallel fanout)
- **low** -- Heavy `.then()` chaining with error recovery, but no custom types

## Architecture

Look for async result containers that decouple task submission from result retrieval.

### Review Checklist

- Every future/promise has an error path -- `.catch()`/`except` handlers are not omitted
- Composition is used for parallel work (`Promise.all`, `asyncio.gather`) rather than sequential awaits in a loop
- Cancellation is supported and propagated through the chain
- Timeouts are applied to prevent indefinite waits on unresolved futures
- Results are consumed -- no orphaned futures whose exceptions go unobserved

### Anti-patterns

- Awaiting futures sequentially in a loop when they could run concurrently
- Swallowing rejections/exceptions with empty `.catch()` handlers
- Creating futures without ever awaiting or observing their result (fire-and-forget with no error handling)
- Mixing callback and promise styles in the same flow, losing error propagation
