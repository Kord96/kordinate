---
description: Graceful Degradation — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Verify degradation paths are functional before relying on them in production, and test them as part of every rollout.

### Rollout Implications

- Deploy degradation fallback logic before the primary path it protects — if the primary fails during rollout, the fallback must already be in place
- Rolling updates may temporarily activate degradation if new pods cannot reach a dependency the old pods could — monitor for transient degradation during rollout
- If changing degradation thresholds, deploy the new thresholds to a canary first to verify they do not trigger false activations
- Test degradation paths in staging before each production deploy — untested fallbacks fail when needed most

### Pre-deploy Checklist

- Verify all degradation fallbacks return acceptable responses (cached data, static defaults) not error pages
- Confirm alerting is active for degradation activation so operators are aware the system is running in reduced mode
