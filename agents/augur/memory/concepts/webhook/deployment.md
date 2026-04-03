---
description: Webhook — deployment guidance
type: supplementary
---
## Deployment

Deploy payload and signing changes with backward compatibility, since consumers update on their own schedule and cannot be force-upgraded.

### Rollout Implications

- Payload format changes must be additive (add fields, never rename or remove) — consumers parse the old format and will break silently on incompatible changes
- Signing secret rotation requires a dual-validation window where both old and new secrets are accepted — deploying a new secret without the overlap immediately invalidates all existing consumer verification
- Scaling down webhook dispatch workers during a deploy reduces delivery throughput — events queue up and may hit retry limits or dead-letter before workers recover
- Deploying retry policy changes affects all in-flight deliveries, not just new ones — tightening retry limits may cause currently-retrying deliveries to be abandoned
- Deprecating a webhook endpoint requires coordinating with external consumers who control their own deployment timeline — removing an endpoint without monitoring usage drops events silently

### Pre-deploy Checklist

- Verify backward compatibility of payload format changes by testing against the previous schema
- Confirm signing secret rotation includes a dual-validation window accepting both old and new secrets
- Ensure dispatch queue workers have enough capacity to handle registered webhook volume after the deploy
- Test delivery retry behavior in staging before deploying retry policy changes to production
- Verify dead-letter handling is deployed and functional before increasing webhook volume or tightening retry limits
