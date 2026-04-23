---
kind: concept
name: cqrs
signatures:
  concept: cqrs
  positive:
    strong:
    - distinct command and query handlers with separate read or write stores
    - explicit projection or synchronization path between models
    medium:
    - handler-level read or write separation with some dedicated read-model machinery
    weak:
    - naming-only separation with no independent projection path
  negative:
  - one shared model serving both reads and writes with no clear separation
  - cache or pagination alone mistaken for a read model
  notes:
  - CQRS is architectural only when the separation changes the system's shape or consistency
    model.
type: pattern
abstraction:
- architectural
- data
scope: cross-cutting
status: primary
review_questions:
  threshold: 6
  entries:
  - id: cqrs-command-query-separation
    prompt: Are command and query paths intentionally separated in handlers, models,
      or stores?
    weight: 3
    signals:
    - CommandHandler
    - QueryHandler
    - command
  - id: cqrs-read-model-sync
    prompt: Is there an explicit read-model projection or sync mechanism rather than
      just naming conventions?
    weight: 3
    signals:
    - projection
    - read model
    - materialized
monitoring:
  applies_to:
  - component
  - flow
  - state
  health_signals:
  - name: cqrs.projection.lag
    description: Delay between write-side mutations and read-model visibility.
  - name: cqrs.projection.error.rate
    description: Failures updating or rebuilding read models.
  business_metrics: []
  gaps:
  - Missing projection lag visibility hides eventual-consistency regressions.
family: design-patterns
---

# Explanation

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

### Relationship To Other Concepts

- Related to [event-sourcing](/concepts/event-sourcing) when the write model records events that later feed projections.
- Related to [search-index](/concepts/search-index) when separate read models are optimized for query-heavy access.
- Related to [change-data-capture](/concepts/change-data-capture) when read-side projections are driven from persistence changes instead of application-level events.

### Boundary

Use `cqrs` when commands and queries are intentionally separated into different models, handlers, or storage paths.

Do not use it for ordinary service layering, caching, or read replicas unless the codebase clearly models separate write and read responsibilities.
