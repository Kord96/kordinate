---
description: Leader Election — deployment guidance
type: supplementary
---
## Deployment

Coordinate rollouts with leader lease lifecycle to avoid split-brain or prolonged leaderless windows.

### Rollout Implications

- Rolling updates should terminate the leader pod last to minimize unnecessary re-elections
- New pods must be able to participate in elections before old pods are terminated (readiness-gated)
- If the leader pod is killed mid-lease, followers should detect the expired lease and elect a new leader within the TTL
- Avoid deploying all replicas simultaneously -- staggered rollout prevents a leaderless gap

### Pre-deploy Checklist

- Verify the lease TTL is shorter than the deployment's pod termination grace period
- Confirm the leader releases its lease on graceful shutdown (preStop hook or signal handler)
- Test that a new version can win elections against the old version without protocol incompatibility
