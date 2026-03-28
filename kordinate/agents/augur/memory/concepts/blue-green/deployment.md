---
description: Blue-Green Deployment — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Maintain two identical environments; deploy to the idle one, verify, then switch traffic atomically.

### Rollout Implications

- Traffic switch is atomic — all users move at once, no gradual rollout
- Database migrations must be backward-compatible since both environments share the data layer
- Keep the old environment running post-switch as an instant rollback target

### Pre-deploy Checklist

- Verify the idle environment mirrors production configuration (env vars, secrets, feature flags)
- Run smoke tests against the idle environment before switching traffic
- Confirm database schema compatibility between both application versions
