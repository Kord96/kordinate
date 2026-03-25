---
description: Cqrs architectural pattern
curated: true
scope: global
preloaded: none
---
# CQRS


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

Track read/write path health and projection lag to catch sync divergence before it becomes user-visible.

### Key Metrics

- `projection_lag_seconds` (gauge) — delay between write model update and read model sync
- `command_processed_total` (counter) — commands handled by the write path
- `query_processed_total` (counter) — queries served by the read path
- `projection_errors_total` (counter) — failures during read model projection/sync
- `projection_rebuild_duration_seconds` (histogram) — time to rebuild read model from scratch

### Alerts

- Projection lag exceeding acceptable consistency window
- Projection error rate spiking (sync mechanism broken)
- Read model rebuild taking longer than maintenance window allows
- Write-to-read ratio diverging unexpectedly (indicates stale projections or lost events)

## Deployment

Read and write model schema changes must be synchronized to avoid projection drift or query failures.

### Rollout Implications

- Write model schema changes must deploy before read model projections that depend on the new fields
- Projection rebuild may be required after deploying new read model schemas — plan for rebuild time and increased load
- During rollout, old pods may serve stale read models while new pods serve updated projections — clients must tolerate temporary inconsistency
- Deploying a new projection alongside the old one (blue-green) avoids downtime but requires sufficient storage for both

### Pre-deploy Checklist

- Verify write model migrations are applied before deploying updated projection logic
- Estimate projection rebuild time and confirm it fits within acceptable staleness windows
- Confirm read model storage has capacity for a full rebuild if required
- Check that query clients handle missing or null fields gracefully during the transition

## Testing

Validate strict read/write separation, projection correctness, and behavior under eventual consistency.

### Unit Tests

- Test that commands modify only the write model — assert no side effects on the read store
- Verify projection logic: given a sequence of domain events, assert the read model reflects the correct denormalized state
- Test that queries return data exclusively from the read model, even when the write model has newer uncommitted state
- Assert that projections handle duplicate events idempotently (replaying the same event does not corrupt the read model)

### Integration Tests

- Issue a command, wait for projection sync, then query the read model and verify consistency with the write
- Rebuild the read model from scratch by replaying all events and assert it matches the incrementally projected state
- Test read model under concurrent writes — multiple commands projecting simultaneously should not produce race conditions

### Failure Injection

- Halt the projection sync process and verify the read model serves stale but valid data without errors
- Simulate projection failure mid-batch and verify it resumes from the correct offset without skipping events
- Drop and rebuild the read store while the write model is active — confirm the projection catches up fully
