---
description: Correlation ID — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Ensure all services propagate correlation IDs consistently, especially during mixed-version rollouts.

### Rollout Implications

- New services must propagate existing correlation IDs from incoming requests, not generate new ones
- During rolling updates, both old and new versions must handle the correlation header identically
- Log format changes must preserve the correlation ID field to maintain traceability across versions

### Pre-deploy Checklist

- Verify the correlation ID header name is consistent across all services in the call chain
- Confirm logging configuration includes the correlation ID in structured log fields
