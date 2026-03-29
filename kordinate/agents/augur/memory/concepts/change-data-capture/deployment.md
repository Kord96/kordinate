---
description: Change Data Capture (CDC) — deployment guidance
type: supplementary
---
## Deployment

Coordinate connector updates with schema changes and ensure no events are lost during rollout.

### Rollout Implications

- Schema changes on the source database must be backward-compatible with the running connector
- Deploy connector updates during low-traffic windows to minimize replication lag during restart
- Connector restart triggers a catch-up phase — consumers may see a burst of events

### Pre-deploy Checklist

- Verify the connector's stored offset is valid and will resume from the correct position
- Test schema compatibility between the new connector version and current source schema
- Confirm consumer idempotency — duplicate events during catch-up must be handled safely
