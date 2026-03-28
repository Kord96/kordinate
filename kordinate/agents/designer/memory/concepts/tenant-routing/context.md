# Testing

- Test tenant resolution from all supported sources (subdomain, header, JWT) and verify correct routing
- Verify that connection pools are bounded per tenant and one tenant cannot exhaust shared resources
- Test routing for unknown or misconfigured tenants — must reject, not route to a default tenant
- Test shard rebalancing: move a tenant between shards and verify requests route correctly afterward
- Verify routing cache behavior: cached routes expire and refresh when tenant mappings change
- Test that routing happens at the edge (gateway/middleware) before any business logic executes
- Load test with many tenants to verify routing performance does not degrade with tenant count
- Test failover: designated backend goes down, verify behavior (error, retry, or fallback)

# Monitoring

- Track per-tenant connection pool utilization and alert when any tenant's pool approaches exhaustion
- Monitor routing decision latency — per-request routing lookups indicate missing caching
- Alert on unknown or misconfigured tenant routing failures (requests that cannot be routed)
- Track tenant-to-shard mapping changes and alert on unexpected rebalancing activity
- Monitor request distribution across backends/shards to detect routing imbalance
- Dashboard showing per-tenant request rates, backend assignments, and routing error rates
- Alert when a tenant's designated backend is unhealthy or unreachable

# Deployment

- Deploy routing configuration changes (shard map, tenant-to-backend mapping) before scaling backends
- Verify that new backend instances are routable before directing tenant traffic to them
- Test routing fallback behavior for unknown tenants in staging before production release
- Coordinate shard rebalancing with application deployments to avoid routing mismatches
- Deploy connection pool configuration changes alongside shard topology updates
- Ensure routing cache invalidation is triggered on deployment of new tenant mappings
- Validate that gateway-level tenant extraction (subdomain, header) works after load balancer changes

