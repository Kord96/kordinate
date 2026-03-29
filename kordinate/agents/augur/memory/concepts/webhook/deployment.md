---
description: Webhook — deployment guidance
type: supplementary
---
# Deployment

- Deploy webhook payload format changes with backward compatibility — add fields, do not rename or remove
- Rotate signing secrets with a dual-validation window: accept both old and new secrets during transition
- Deploy dispatch queue workers with enough capacity to handle the registered webhook volume
- Verify webhook endpoint validation (URL reachability or ownership proof) after any registration changes
- Test delivery retry behavior in staging before deploying retry policy changes to production
- Coordinate webhook deprecation with consumers: announce timeline, monitor old endpoint usage, then remove
- Ensure dead-letter handling is deployed and tested before increasing webhook volume
