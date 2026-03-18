# CQRS

```
               Commands                          Queries
                  │                                 ▲
                  ▼                                 │
           ┌────────────┐                    ┌────────────┐
           │   Write    │     events /       │    Read    │
           │   Model    │────projections────►│   Model    │
           │            │                    │            │
           │(normalized,│                    │(denormalized│
           │ consistent)│                    │  fast reads)│
           └────────────┘                    └────────────┘
                  │               ▲                 │
                  ▼               │                 ▼
            Write Store     Event Bridge       Read Store
```

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

## Monitoring

TODO

## Deployment

TODO

## Testing

TODO
