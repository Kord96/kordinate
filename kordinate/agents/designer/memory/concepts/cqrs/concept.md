---
description: CQRS architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [architectural, data]
---
# CQRS


## Recognition

How to identify this pattern in code.

### Signatures

- Separate `CommandHandler` and `QueryHandler` classes or interfaces
- `@CommandHandler` and `@QueryHandler` annotations (Axon Framework)
- MediatR `IRequest<T>` and `IRequestHandler<TRequest, TResponse>` with distinct command/query request types (.NET)
- Separate read and write repository interfaces (e.g., `WriteRepository`, `ReadRepository` or `CommandStore`, `QueryStore`)
- Separate database connections or data sources for read operations vs write operations

### Confidence

- **high** -- explicit command/query separation with distinct handlers, separate read/write stores, and a projection or sync mechanism between them
- **medium** -- separate handler classes for reads and writes but both using the same underlying database or store
- **low** -- read-heavy endpoints using a cache or materialized view alongside a primary write store, but no formal command/query separation in code

## Architecture

Look for strict separation between write and read paths with an explicit sync mechanism.

### Review Checklist

- Commands mutate only the write model — no direct writes to the read store
- Queries read only from the read model — never from the write store
- Projection/sync mechanism is explicit and observable (not ad-hoc cache fills)
- Eventual consistency is documented and acceptable for the use case
- Read model can be rebuilt from scratch (replayable projections)

### Anti-patterns

- Read path sneaking writes back into the write model
- No clear sync mechanism — read model silently drifts from write model
- Applying CQRS where a single model would suffice (unnecessary complexity)
