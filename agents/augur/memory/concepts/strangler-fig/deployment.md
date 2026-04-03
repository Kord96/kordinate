---
description: Strangler Fig — deployment guidance
type: supplementary
---
## Deployment

Deploy the routing layer first and migrate features one at a time, always preserving the ability to fall back to the legacy system.

### Rollout Implications

- The routing layer (proxy, gateway, feature flag) must be deployed and stable before migrating any feature — it is the control surface for the entire migration
- Each migrated feature should be deployed, traffic-shifted, and verified independently — migrating multiple features simultaneously makes it impossible to isolate which one caused a regression
- Dual-write periods require both old and new data stores to receive writes simultaneously — if one side fails during a deploy, data diverges silently without reconciliation checks
- Rolling back a migrated feature means switching the route back to legacy — if the legacy code path has degraded or been partially decommissioned, rollback may not work cleanly
- The strangler proxy itself accumulates routing rules over time — deploying changes to it becomes increasingly risky as it grows in complexity

### Pre-deploy Checklist

- Verify that each migrated feature has an independent rollback toggle to fall back to legacy
- Run reconciliation checks during dual-write periods to detect data drift between old and new stores
- Confirm the legacy system is still functional for any features that may need to be rolled back
- Track migration progress as a deployment metric: percentage of traffic or features on the new system
- Define a decommissioning plan for the legacy system — do not let the strangler proxy become permanent infrastructure
