# Event Sourcing — Design Perspective

```
  Command ──► Aggregate ──► Event(s) ──► Event Store
                                              │
                 ┌────────────────────────────┘
                 │ replay
                 ▼
            Current State ◄── Snapshot (optional, for long histories)
                 │
                 ▼
            Read Model (projection for queries)
```

Look for correct event modeling and state reconstruction.

## Review Checklist

- Events are immutable facts, named in past tense (OrderPlaced, not PlaceOrder)
- Aggregate state is derived solely from replaying events — no side-channel writes
- Event schema includes a version field for future evolution
- Snapshots exist for aggregates with long event histories

## Anti-patterns

- Mutable events or events that reference other events by content
- Business logic in the event store layer
- Missing event versioning — schema changes break replay
