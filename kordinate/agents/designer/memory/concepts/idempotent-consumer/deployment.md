---
description: Idempotent Consumer — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Coordinate deployments with message redelivery behavior to avoid false duplicates or missed dedup.

### Rollout Implications

- During rolling updates, old and new consumer versions may process the same message -- both must write to the same idempotency store
- Schema changes to the idempotency store (inbox table) must be backward-compatible with the running version
- If switching idempotency backends (e.g., in-memory to database), run both in parallel during transition to avoid gaps

### Pre-deploy Checklist

- Verify the idempotency store migration has been applied before deploying the new consumer version
- Confirm TTL cleanup jobs are scheduled and running in the target environment
- Check that the processed-ID store is shared across all consumer replicas, not local to each pod
