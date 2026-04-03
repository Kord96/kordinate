---
description: Service Mesh — deployment guidance
type: supplementary
---
## Deployment

Upgrade the control plane and data plane sidecars in the correct order, and verify that security policies survive the transition.

### Rollout Implications

- Control plane must be upgraded before data plane sidecars — new proxy versions may depend on control plane APIs that the old version does not serve
- Rolling sidecar restarts cause brief connection drops between services — during the restart window, mTLS handshakes may fail between old and new proxy versions
- mTLS enforcement mode can silently revert to permissive after a control plane upgrade, allowing plaintext traffic without alerting
- Sidecar resource limits that are not set explicitly in the deployment manifest may change after an upgrade, causing proxy resource contention or OOM kills
- Traffic policies (retries, timeouts, circuit breaking) configured at the mesh level may behave differently with a new proxy version — compounding with application-level settings

### Pre-deploy Checklist

- Verify mTLS enforcement mode after control plane upgrade — confirm it has not reverted to permissive
- Set explicit sidecar resource limits in deployment manifests to prevent proxy starvation
- Test traffic policies in staging with the new proxy version before promoting to production
- Confirm sidecar injection is working for new pods after control plane upgrades
- Coordinate namespace-level authorization policy changes with the teams owning affected services
