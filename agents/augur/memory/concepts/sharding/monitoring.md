---
description: Sharding — monitoring guidance
type: supplementary
---
# Monitoring

- Track data distribution across shards — alert on skew where one shard holds disproportionately more data
- Monitor per-shard query latency and throughput to detect hot shards under uneven load
- Alert on cross-shard query frequency — high scatter-gather rates indicate shard key misalignment
- Track per-shard connection pool utilization and alert when any shard pool approaches exhaustion
- Monitor shard rebalancing operations: duration, data migrated, and impact on query latency
- Dashboard showing shard sizes, query rates, and connection counts side by side
- Alert on shard health — a single unhealthy shard affects a partition of the user base
