---
description: Sharding — deployment guidance
type: supplementary
---
## Deployment

Synchronize shard map changes with application deployments to prevent routing mismatches while old and new code coexist.

### Rollout Implications

- Shard routing changes (new shard map) must be deployed before adding or removing shard nodes — the application must know where to route before the topology changes
- During rolling deployments, old and new application code coexist — the shard router must be backward-compatible so both versions route correctly
- Rebalancing shards while a rollout is in progress creates two simultaneous sources of instability — data is migrating while the application code is changing
- Adding shards without updating connection pool configuration causes new shards to be unreachable — connection pools must match the new shard count before enabling traffic
- Dual-read during migration (reading from both old and new shard locations) doubles read load temporarily — capacity must account for this

### Pre-deploy Checklist

- Verify connection pool configuration matches the new shard count
- Test rebalancing in staging with production-like data volumes before executing in production
- Confirm the shard router handles both old and new shard maps during the rolling window
- Prepare a rollback plan for the shard map that is independent of the application rollback
- Monitor query error rates per shard during topology changes
