---
description: Claim Check — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Ensure the external store is available before deploying services that read or write claim references.

### Rollout Implications

- The blob/object store must be accessible from both old and new service versions during rollout
- Claim reference format changes require coordination between producer and consumer deployments
- Rolling restart may leave unretrieved claims in the store — ensure retention policy covers rollout duration

### Pre-deploy Checklist

- Verify external store connectivity and permissions from the target deployment environment
- Confirm claim TTL and cleanup policies will not expire payloads during extended rollouts
