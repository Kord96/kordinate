---
description: Strangler Fig — deployment guidance
type: supplementary
---
# Deployment

- Deploy the routing layer (proxy, gateway, feature flag) before migrating any features
- Migrate one feature at a time — deploy the new service, route traffic, verify, then move to the next
- Ensure each migrated feature has an independent rollback toggle to fall back to legacy
- Coordinate dual-write deployments carefully: both old and new stores must be written simultaneously
- Run reconciliation checks during dual-write periods to detect data drift between old and new stores
- Track migration progress as a deployment metric: percentage of traffic or features on the new system
- Plan for decommissioning the legacy system — do not let the strangler proxy become permanent infrastructure
