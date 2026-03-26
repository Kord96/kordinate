---
description: Sharding architectural pattern
curated: true
scope: global
preloaded: none
---
# Sharding

## Recognition

How to identify this pattern in code.

### Signatures

- Shard key selection and shard ID derivation logic
- Consistent hashing or hash-ring implementations
- Shard router/resolver that maps keys to database connections or partitions
- Partition-aware queries with shard hints or routing decorators
- `shard_key`, `partition_key`, or `tenant_id` fields on models or tables
- Multiple database connection configurations (shard_0, shard_1, etc.)
- Rebalancing or migration tooling for shard splits

### Confidence

- **high** -- explicit shard router with consistent hashing and per-shard connection pools
- **medium** -- database partitioning configured at the schema level (PostgreSQL partitions, Vitess)
- **low** -- multiple databases used per tenant but without formal shard routing logic

## Architecture

Look for data distributed across multiple storage nodes with a deterministic routing layer that maps keys to shards.

### Review Checklist

- Shard key is immutable and evenly distributes data (avoids hot shards)
- Cross-shard queries are identified and handled explicitly (scatter-gather or denormalization)
- Shard routing is centralized, not duplicated across services
- Rebalancing strategy exists for adding or removing shards without downtime
- Connection pool management scales per-shard, not globally

### Anti-patterns

- Choosing a shard key that causes skewed distribution (all data on one shard)
- Cross-shard joins treated as normal queries (hidden N+1 across shards)
- No plan for resharding when shard count needs to change
- Application logic assuming data locality across shard boundaries
