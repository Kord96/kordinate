---
description: Event-Carried State Transfer — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
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
