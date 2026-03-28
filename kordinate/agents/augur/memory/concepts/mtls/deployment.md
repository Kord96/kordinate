---
description: Mutual TLS — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Coordinate certificate provisioning with service rollouts to avoid handshake failures during deployment.

### Rollout Implications

- New service versions must have valid client certificates provisioned before they attempt connections
- CA bundle updates must be deployed to servers before clients present certificates signed by the new CA
- Rolling updates should maintain at least one pod with a valid certificate at all times during transition
- Certificate rotation and service deployment should not overlap to isolate failure causes

### Pre-deploy Checklist

- Verify client and server certificates are provisioned and not expired in the target environment
- Confirm the CA bundle on the server includes the CA that signed the new client certificates
- Test mTLS handshake between the new service version and its dependencies in a staging environment
- Ensure plaintext fallback is disabled -- TLS enforcement is not optional
