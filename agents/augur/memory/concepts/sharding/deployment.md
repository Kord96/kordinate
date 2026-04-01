---
description: Sharding — deployment guidance
type: supplementary
---
# Deployment

- Deploy shard routing changes (new shard map) before adding or removing shard nodes
- Roll shard migrations with a dual-read strategy: read from both old and new locations during transition
- Verify connection pool configuration matches the new shard count before enabling traffic
- Test rebalancing in staging with production-like data volumes before executing in production
- Coordinate application deployments with shard topology changes to avoid routing mismatches
- Ensure the shard router is backward-compatible during rolling deployments (old and new code coexist)
- Monitor query error rates during shard topology changes and have a rollback plan for the shard map
