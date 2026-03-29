---
description: Tenant-Aware Routing — testing guidance
type: supplementary
---
# Testing

- Test tenant resolution from all supported sources (subdomain, header, JWT) and verify correct routing
- Verify that connection pools are bounded per tenant and one tenant cannot exhaust shared resources
- Test routing for unknown or misconfigured tenants — must reject, not route to a default tenant
- Test shard rebalancing: move a tenant between shards and verify requests route correctly afterward
- Verify routing cache behavior: cached routes expire and refresh when tenant mappings change
- Test that routing happens at the edge (gateway/middleware) before any business logic executes
- Load test with many tenants to verify routing performance does not degrade with tenant count
- Test failover: designated backend goes down, verify behavior (error, retry, or fallback)
