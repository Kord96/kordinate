---
kind: concept
name: future-promise
signatures: {}
type: pattern
abstraction:
- concurrency
- design
scope: backend
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Deferred computation represented as a handle to a result not yet available
- `.then()`, `await`, `.get()`, `.result()` calls on async result containers
- `Future`, `Promise`, `CompletableFuture`, `Deferred`, `Task` types
- Chaining and composition: `Promise.all()`, `asyncio.gather()`, `CompletableFuture.thenCompose()`
- Libraries: JavaScript `Promise`, Python `asyncio.Future`/`concurrent.futures.Future`, Java `CompletableFuture`, Rust `Future` trait

### Confidence

- **high** -- Explicit `Future`/`Promise` objects with `.then()` chains or `await` suspension points
- **medium** -- Callback-based async operations returning a handle that resolves later
- **low** -- Any deferred computation pattern where results are retrieved asynchronously

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

### Relationship To Other Concepts

- Related to [callback-hell](/concepts/callback-hell) because futures and promises are a common abstraction for flattening nested async callbacks.
- Related to [request-reply](/concepts/request-reply) when asynchronous requests resolve later into a promised response.
- Related to [reactor](/concepts/reactor) because event-loop systems frequently expose readiness outcomes through future-like abstractions.

### Boundary

Use `future-promise` when asynchronous work returns a deferred handle that will eventually resolve to a value or error.

Do not use it for synchronous wrappers, generic callbacks, or queue-based work without a promised completion handle.
