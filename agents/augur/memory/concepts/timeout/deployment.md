---
description: Timeout — deployment guidance
type: supplementary
---
## Deployment

Review timeout values whenever network topology or dependencies change, and keep timeout configuration decoupled from feature deployments.

### Rollout Implications

- Adding a new downstream dependency without adjusting the caller's timeout can cause the caller to time out before the dependency responds under normal load
- During rolling deployments, old and new pods may have different timeout values — if the new code has a shorter timeout, it may start failing on calls that the old code tolerates
- Timeout changes interact with circuit breaker and retry configurations — lowering a timeout without adjusting retry count can cause more retries within the same wall-clock budget, compounding load on the dependency
- Deploying timeout changes alongside feature changes makes it impossible to isolate whether errors are from the new feature or the new timeout value
- Deadline propagation must be consistent across the call chain after a deploy — if a parent service tightens its deadline but a child service is not yet redeployed, the child may outlive the parent's deadline

### Pre-deploy Checklist

- Confirm downstream service timeouts are shorter than the upstream caller's timeout at every hop in the call chain
- Verify timeout values are configurable via environment or config, not requiring a code deploy to change
- Test timeout behavior in staging under realistic latency conditions
- Review interaction between timeout, retry, and circuit breaker settings to avoid compounding failures
- Monitor timeout error rates during and after deployment to catch misconfigured values early
