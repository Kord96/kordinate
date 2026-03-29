---
description: Event Sourcing — deployment guidance
---
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
