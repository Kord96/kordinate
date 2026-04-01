---
description: Choreography — deployment guidance
---
## Deployment

Event schema versioning and consumer deployment ordering determine whether the event chain breaks during rollout.

### Rollout Implications

- Deploy consumers before producers when introducing new event fields — consumers must be able to handle the new schema before events arrive
- Event schema changes must be backward-compatible (additive only) since old and new consumers run simultaneously during rollout
- Deploying a producer that emits a new event type before any consumer exists creates unprocessed event buildup
- Rolling back a single service may break the choreography if other services have already adapted to its new event schema

### Pre-deploy Checklist

- Verify event schema changes are backward-compatible (no removed or renamed fields)
- Confirm all downstream consumers are deployed and ready before upstream producers emit new event types
- Check that correlation ID propagation is intact across all services involved in the rollout
