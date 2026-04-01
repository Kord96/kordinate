---
description: Tenant-Aware Routing — monitoring guidance
type: supplementary
---
# Monitoring

- Track per-tenant connection pool utilization and alert when any tenant's pool approaches exhaustion
- Monitor routing decision latency — per-request routing lookups indicate missing caching
- Alert on unknown or misconfigured tenant routing failures (requests that cannot be routed)
- Track tenant-to-shard mapping changes and alert on unexpected rebalancing activity
- Monitor request distribution across backends/shards to detect routing imbalance
- Dashboard showing per-tenant request rates, backend assignments, and routing error rates
- Alert when a tenant's designated backend is unhealthy or unreachable
