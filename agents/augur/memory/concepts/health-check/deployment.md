---
description: Health Check — deployment guidance
type: supplementary
---
## Deployment

Ensure probes are tuned for the rollout strategy and slow-starting services do not get killed prematurely.

### Rollout Implications

- Configure startup probes for slow-starting applications to prevent liveness failures during initialization
- Set `initialDelaySeconds` on readiness probes so new pods are not expected to serve traffic before startup completes
- Rolling updates should wait for readiness before proceeding to the next pod (maxUnavailable and maxSurge tuning)
- Verify that liveness probes do not check external dependencies -- a database outage should not restart all pods

### Pre-deploy Checklist

- Confirm probe timeouts are shorter than probe periods to avoid overlapping checks
- Validate that readiness probe failure removes the pod from the Service endpoint list without killing it
- Test that a new deployment rolls back automatically when readiness probes fail consistently
