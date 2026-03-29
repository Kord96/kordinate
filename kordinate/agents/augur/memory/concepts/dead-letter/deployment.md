---
description: Dead Letter Queue — deployment guidance
type: supplementary
---
## Deployment

Ensure DLQ infrastructure is provisioned before consumer changes and that message format compatibility is maintained.

### Rollout Implications

- Deploy DLQ consumers and replay tooling before deploying producer changes that may alter message schemas
- Rolling updates to consumers may temporarily increase DLQ volume if new code rejects messages the old code accepted
- Verify DLQ retention policies are long enough to survive a rollout window plus investigation time
- If changing message format, ensure the DLQ consumer can deserialize both old and new formats during transition

### Pre-deploy Checklist

- Confirm DLQ topic/queue exists and has correct permissions in the target environment
- Verify alerting is active on DLQ depth so new failures are caught immediately post-deploy
