---
description: Sidecar — deployment guidance
---
## Deployment

Sidecar and main container version coordination is critical — mismatched versions can break shared interfaces.

### Rollout Implications

- Sidecar and main container images are updated together in a pod spec — ensure both versions are tested as a pair before rollout
- Sidecar must be ready before the main container starts serving if the main container depends on it (e.g., Envoy proxy) — use container startup ordering
- Shared volume mounts between sidecar and main container must have compatible file formats across versions
- Updating the sidecar image across the fleet (e.g., Istio proxy upgrade) restarts every pod — plan for fleet-wide rolling restart impact

### Pre-deploy Checklist

- Verify sidecar and main container version compatibility is tested together in staging
- Confirm shared volume mount paths and file format expectations match between sidecar and main container versions
- Check that pod disruption budgets account for fleet-wide restarts when upgrading a sidecar used across many services
