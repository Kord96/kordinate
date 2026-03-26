---
description: Tenant-Aware Routing — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Deployment

- Deploy routing configuration changes (shard map, tenant-to-backend mapping) before scaling backends
- Verify that new backend instances are routable before directing tenant traffic to them
- Test routing fallback behavior for unknown tenants in staging before production release
- Coordinate shard rebalancing with application deployments to avoid routing mismatches
- Deploy connection pool configuration changes alongside shard topology updates
- Ensure routing cache invalidation is triggered on deployment of new tenant mappings
- Validate that gateway-level tenant extraction (subdomain, header) works after load balancer changes
