## Testing

Ensure event replay produces consistent state and that schema evolution does not break reconstruction.

### Unit Tests

- Replay a known sequence of events and assert the resulting aggregate state matches expected values exactly
- Test snapshot + replay: load a snapshot, apply subsequent events, and verify state matches full replay from scratch
- Verify event schema versioning — apply an upcaster to a v1 event and assert it produces a valid v2 event
- Test that applying an invalid event (wrong aggregate, bad sequence number) is rejected by the aggregate

### Integration Tests

- Write events to the real event store, rebuild aggregate state, and compare against expected projections
- Test full replay from an empty state across a large event history — verify correctness and measure rebuild time
- Verify that two concurrent commands on the same aggregate produce an optimistic concurrency conflict, not corrupted state

### Failure Injection

- Corrupt a single event in the store and verify replay detects the inconsistency rather than silently producing wrong state
- Simulate event store unavailability mid-write and confirm no partial event batches are persisted
- Delete a snapshot and verify the system rebuilds state correctly from the full event history

## Monitoring

Track event store throughput, replay performance, and snapshot health to prevent unbounded growth from degrading the system.

### Key Metrics

- `event_store_append_total` (counter) — events written per aggregate type
- `event_store_append_duration_seconds` (histogram) — write latency to the event store
- `event_replay_duration_seconds` (histogram) — time to rebuild aggregate state from events
- `snapshot_age_seconds` (gauge) — time since last snapshot per aggregate type
- `events_since_snapshot` (gauge) — event count since last snapshot per aggregate

### Alerts

- Event replay duration exceeding acceptable threshold (snapshot may be stale or missing)
- Events-since-snapshot count growing beyond configured limit
- Event store append latency degrading (storage pressure)
- Snapshot creation failures accumulating

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

