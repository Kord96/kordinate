## Testing

Verify that consumers correctly build and maintain local state projections from event streams.

### Unit Tests

- Apply a sequence of events to a consumer and assert the resulting local state matches the expected projection
- Test idempotency: replaying the same event should not corrupt or duplicate local state
- Verify that events with missing optional fields are handled gracefully with defaults
- Test out-of-order delivery: consumer should either reorder or reject events that violate causality

### Integration Tests

- Publish a stream of state-carrying events and verify the consumer's local store matches the producer's authoritative state
- Test schema evolution: publish events in the old format and new format and confirm the consumer handles both
- Verify that a full replay from the event log produces the same local state as incremental consumption

### Consistency Tests

- Compare the consumer's local projection against the source of truth after a burst of concurrent updates to detect drift

## Deployment

Manage schema evolution carefully since consumers maintain local copies of state derived from event payloads.

### Rollout Implications

- Deploy consumers that handle the new event schema before deploying producers that emit it — consumers must tolerate unknown fields
- State rebuild from event replay may be needed if the local projection schema changes — plan for backfill time in the rollout window
- Rolling updates may cause consumers to temporarily hold divergent local state versions — ensure reads tolerate eventual consistency
- If adding new fields to events, use additive-only changes; removing fields requires a deprecation period

### Pre-deploy Checklist

- Verify that the event schema registry (if used) contains the new version and compatibility checks pass
- Confirm consumers can rebuild local state from the event log within acceptable time if a full replay is needed

