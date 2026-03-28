---
description: Distributed Lock — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Coordinate rollouts carefully since lock semantics depend on consistent behavior across all nodes.

### Rollout Implications

- Rolling updates mean old and new code may compete for the same locks — ensure lock key naming and TTL semantics are unchanged or backward-compatible
- If changing lock TTL, deploy the increase first; a decreased TTL on new nodes while old nodes hold longer locks can cause premature expiry assumptions
- Verify the lock backend (Redis, ZooKeeper, etcd) is healthy before starting the rollout — degraded coordination makes lock behavior unpredictable
- Drain work from nodes before termination to avoid locks being held by dying processes

### Pre-deploy Checklist

- Confirm lock backend quorum is intact and latency is within normal bounds
- Verify fencing tokens or lock versioning is in place to prevent stale lock holders from making writes
