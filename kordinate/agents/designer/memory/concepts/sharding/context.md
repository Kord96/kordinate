# Testing

- Test shard key routing: verify the same key always resolves to the same shard deterministically
- Test data distribution with synthetic keys to confirm even spread across shards (no hot shard)
- Verify cross-shard queries return correct results via scatter-gather or denormalization paths
- Test shard addition and removal: add a new shard, rebalance, and verify data accessibility
- Test shard router behavior when a shard is unreachable (timeout, fallback, or clear error)
- Assert that shard routing is centralized — no duplicate routing logic across services
- Test concurrent writes to different shards to verify connection pool isolation
- Load test with realistic shard key distributions to detect performance cliffs on skewed data

# Monitoring

- Track data distribution across shards — alert on skew where one shard holds disproportionately more data
- Monitor per-shard query latency and throughput to detect hot shards under uneven load
- Alert on cross-shard query frequency — high scatter-gather rates indicate shard key misalignment
- Track per-shard connection pool utilization and alert when any shard pool approaches exhaustion
- Monitor shard rebalancing operations: duration, data migrated, and impact on query latency
- Dashboard showing shard sizes, query rates, and connection counts side by side
- Alert on shard health — a single unhealthy shard affects a partition of the user base

# Deployment

- Deploy shard routing changes (new shard map) before adding or removing shard nodes
- Roll shard migrations with a dual-read strategy: read from both old and new locations during transition
- Verify connection pool configuration matches the new shard count before enabling traffic
- Test rebalancing in staging with production-like data volumes before executing in production
- Coordinate application deployments with shard topology changes to avoid routing mismatches
- Ensure the shard router is backward-compatible during rolling deployments (old and new code coexist)
- Monitor query error rates during shard topology changes and have a rollback plan for the shard map

