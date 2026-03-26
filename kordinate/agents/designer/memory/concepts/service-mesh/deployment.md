---
description: Service Mesh — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Deployment

- Upgrade the mesh control plane before data plane sidecars — control plane must support the new proxy version
- Roll sidecar updates gradually using a canary or rolling restart to avoid fleet-wide proxy issues
- Verify mTLS mode after upgrade — confirm enforcement has not reverted to permissive
- Set sidecar resource limits explicitly in the deployment manifest to prevent proxy resource contention
- Test traffic policies (retries, timeouts, circuit breaking) in staging before promoting to production
- Coordinate namespace-level authorization policy changes with the teams owning affected services
- Validate that sidecar injection is working for new pods after control plane upgrades
