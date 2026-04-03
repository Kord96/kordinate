---
description: Sharding — monitoring guidance
---
## Monitoring

Track data distribution, per-shard performance, and cross-shard query patterns to maintain balanced throughput.

### Key Metrics

- `shard_data_size_bytes` (gauge) — data volume per shard, surfaces distribution skew
- `shard_query_latency_seconds` (histogram) — per-shard query latency to detect hot shards
- `shard_query_rate` (counter) — queries per second per shard, reveals load imbalance
- `shard_connection_pool_utilization` (gauge) — active connections as a fraction of pool capacity per shard
- `shard_cross_shard_queries_total` (counter) — scatter-gather operations indicating shard key misalignment
- `shard_rebalance_duration_seconds` (histogram) — time spent on shard rebalancing operations

### Alerts

- Single shard holding disproportionately more data than peers (skewed distribution)
- Per-shard latency or throughput diverging significantly from the cluster average (hot shard)
- Connection pool approaching exhaustion on any individual shard
- High cross-shard query rate (shard key does not match access patterns)
- Shard health check failing (affects an entire partition of the user base)
