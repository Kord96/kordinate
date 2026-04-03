---
description: Tenant-Aware Routing — monitoring guidance
---
## Monitoring

Track routing accuracy, per-tenant backend health, and connection pool utilization across the routing layer.

### Key Metrics

- `tenant_routing_decisions_total` (counter) — routing lookups partitioned by tenant and target backend
- `tenant_routing_latency_seconds` (histogram) — time to resolve tenant-to-backend mapping per request
- `tenant_routing_failures_total` (counter) — requests that could not be routed (unknown or misconfigured tenant)
- `tenant_connection_pool_utilization` (gauge) — active connections as a fraction of pool capacity per tenant
- `tenant_routing_mapping_changes_total` (counter) — tenant-to-shard mapping updates from rebalancing events
- `tenant_backend_request_distribution` (gauge) — request rate per backend to detect routing imbalance

### Alerts

- Routing failure for an unknown or misconfigured tenant (requests cannot reach a backend)
- Per-tenant connection pool approaching exhaustion
- Routing decision latency elevated (missing cache or per-request database lookup)
- Tenant's designated backend is unhealthy or unreachable
- Unexpected tenant-to-shard mapping change outside of a planned rebalance window
