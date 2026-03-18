# Event Sourcing

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

## Architecture

Look for correct event modeling and state reconstruction.

### Review Checklist

- Events are immutable facts, named in past tense (OrderPlaced, not PlaceOrder)
- Aggregate state is derived solely from replaying events — no side-channel writes
- Event schema includes a version field for future evolution
- Snapshots exist for aggregates with long event histories

### Anti-patterns

- Mutable events or events that reference other events by content
- Business logic in the event store layer
- Missing event versioning — schema changes break replay

## Monitoring

TODO

## Deployment

Handle event store migrations and replay behavior during rollouts.

### Rollout Implications

- Event schema changes require versioned events — deploy consumers that read both old and new versions before deploying producers that write new versions
- Replay during rollout: if a new version triggers a full replay, expect increased load on the event store — scale accordingly
- Snapshot invalidation: schema changes may invalidate existing snapshots — plan for snapshot rebuild time
- Blue-green deployments are safer than rolling updates for event schema migrations

### Pre-deploy Checklist

- Confirm backward-compatible event schema (old consumers can read new events)
- Verify snapshot rebuild time fits within maintenance window if snapshots are invalidated

## Testing

TODO
