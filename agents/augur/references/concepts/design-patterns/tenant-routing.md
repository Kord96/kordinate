---
kind: concept
name: tenant-routing
signatures: {}
source:
  memory_concept: memory/catalog/concepts/tenant-routing.md
type: pattern
abstraction:
- security
- integration
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Subdomain extraction: parsing tenant from `{tenant}.example.com`, `Host` header splitting
- `X-Tenant-ID` header injection or extraction at the gateway/load balancer layer
- Tenant-specific connection pools: `ConnectionPool.for_tenant(id)`, pool registry keyed by tenant
- Shard router: `ShardRouter.route(tenant_id)`, consistent hashing by tenant, shard map lookup
- Tenant config lookup: `TenantConfig.get(tenant_id)`, feature flags per tenant, tier-based routing
- Multi-database connection switching: `use_database(tenant.db_name)`, `router.db_for_read(tenant)`
- Tenant-based request routing at reverse proxy or service mesh level (Nginx, Envoy, Istio)

### Confidence

- **high** -- gateway extracts tenant, routes to tenant-specific backend or shard, with connection pool per tenant
- **medium** -- tenant ID extracted from request and used to select a database connection, but routing is application-level only
- **low** -- tenant identifier present in routing config but actual request routing does not vary by tenant

## Architecture

Look for a clear routing layer that maps tenant identity to the correct backend, database, or shard before business logic executes.

### Review Checklist

- Tenant resolution happens at the edge (gateway, load balancer, or first middleware) before any business logic
- Connection pools are bounded per tenant to prevent one tenant from exhausting shared resources
- Routing decisions are cached or precomputed -- no per-request database lookups for tenant config
- Fallback behavior is defined for unknown or misconfigured tenants (reject, not route to default)
- Shard mappings support rebalancing without downtime (migration path for moving tenants between shards)

### Anti-patterns

- Resolving tenant routing in business logic instead of infrastructure/middleware
- Unbounded connection pools per tenant that scale with tenant count and exhaust database connections
- Hardcoded tenant-to-shard mappings with no migration path for rebalancing
- No validation of tenant routing -- requests silently route to a wrong or default tenant on lookup failure

### Relationship To Other Concepts

- Related to [tenant-isolation](/concepts/tenant-isolation) because correct routing is often the first step in preserving tenant boundaries.
- Related to [sharding](/concepts/sharding) when tenant identity determines shard, cluster, or schema placement.
- Related to [multi-tenant](/concepts/multi-tenant) because tenant routing is one common infrastructure concern in multi-tenant systems.

### Boundary

Use `tenant-routing` when incoming requests or work items are directed to tenant-specific infrastructure, schemas, shards, or contexts based on tenant identity.

Do not use it for generic authorization or filtering. The key signal is request path or infrastructure routing by tenant.
