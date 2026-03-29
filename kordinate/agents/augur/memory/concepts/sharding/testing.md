---
description: Sharding — testing guidance
type: supplementary
---
# Testing

- Test shard key routing: verify the same key always resolves to the same shard deterministically
- Test data distribution with synthetic keys to confirm even spread across shards (no hot shard)
- Verify cross-shard queries return correct results via scatter-gather or denormalization paths
- Test shard addition and removal: add a new shard, rebalance, and verify data accessibility
- Test shard router behavior when a shard is unreachable (timeout, fallback, or clear error)
- Assert that shard routing is centralized — no duplicate routing logic across services
- Test concurrent writes to different shards to verify connection pool isolation
- Load test with realistic shard key distributions to detect performance cliffs on skewed data
