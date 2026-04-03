---
description: Tenant-Aware Routing — deployment guidance
type: supplementary
---
## Deployment

Deploy routing configuration changes before backend topology changes, and verify that tenant resolution works end-to-end after every infrastructure change.

### Rollout Implications

- Routing configuration (shard map, tenant-to-backend mapping) must be deployed before scaling or removing backends — new pods must be routable before they receive tenant traffic
- Routing cache invalidation must trigger on deployment of new tenant mappings — stale cache entries send tenants to old backends that may no longer exist
- Load balancer or gateway changes can break tenant extraction from subdomains or headers — a deploy that changes host parsing silently misroutes all tenants
- Shard rebalancing during an application rollout creates two simultaneous changes to the routing path — one from the new code, one from the new shard map
- Unknown or misconfigured tenants should be explicitly rejected, not silently routed to a default backend — deploying new tenants without updating the routing map causes silent misrouting

### Pre-deploy Checklist

- Verify that new backend instances are registered in the routing map and reachable before directing tenant traffic
- Test routing fallback behavior for unknown tenants in staging
- Confirm routing cache invalidation fires correctly after deploying new tenant mappings
- Validate tenant extraction from subdomains and headers after any load balancer or gateway changes
- Coordinate shard rebalancing separately from application deployments to avoid compounding routing changes
