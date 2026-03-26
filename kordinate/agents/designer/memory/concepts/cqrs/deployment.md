---
description: CQRS — deployment guidance
curated: true
scope: global
preloaded: none
---
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
