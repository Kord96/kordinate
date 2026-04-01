---
description: Outbox — deployment guidance
type: supplementary
---
## Deployment

Coordinate database schema changes and publisher process lifecycle during rollouts.

### Rollout Implications

- Schema migrations adding columns to the outbox table must be backward-compatible (new columns nullable or with defaults)
- The publisher process must be running during and after deployment -- ensure it is not accidentally terminated during rollout
- If using CDC (Debezium), connector configuration must be updated before schema changes that alter the outbox table structure
- Rolling deployments may produce outbox events in both old and new formats -- consumers must handle both during transition

### Pre-deploy Checklist

- Verify the outbox publisher is healthy and the unpublished count is near zero before starting rollout
- Confirm database migration does not lock the outbox table for extended periods (use online DDL where possible)
- Ensure the message broker topic exists and has appropriate retention for the new event types
- Test that new outbox event formats are deserializable by all downstream consumers before deploying the producer
