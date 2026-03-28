---
description: gRPC/RPC — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Manage proto schema compatibility and connection draining to avoid broken RPCs during rollouts.

### Rollout Implications

- gRPC uses persistent HTTP/2 connections — clients may not discover new server pods until connections are recycled or load balancer drains them
- Deploy backward-compatible proto changes first (additive fields only); breaking changes require a versioned service or two-phase rollout
- Drain in-flight RPCs before terminating pods — configure preStop hooks and terminationGracePeriodSeconds to allow streams to complete
- If using client-side load balancing, clients must re-resolve DNS or endpoints after server pods roll

### Pre-deploy Checklist

- Verify proto compatibility: new server can handle requests from old clients and vice versa
- Confirm health check and reflection services are registered on the new build
- Check that TLS certificates (if using mTLS) are valid and match the new pod identity
