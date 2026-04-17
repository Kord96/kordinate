---
description: Tenant Isolation architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction:
- security
- data
status: primary
scope: domain
relationships:
  related_to:
  - tenant-routing
  - multi-tenant
  - rbac
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Tenant Isolation

## Recognition

How to identify this pattern in code.

### Signatures

- Tenant ID in request context: `request.tenant_id`, `ctx.tenant`, `TenantContext.current()`
- `tenant_id` column in database tables, foreign key or partition key
- Schema-per-tenant: `SET search_path TO tenant_<id>`, dynamic schema selection
- Database-per-tenant: tenant-specific connection strings, connection pool per tenant
- Row-level security policies: `CREATE POLICY`, `ENABLE ROW LEVEL SECURITY`, `SET app.current_tenant`
- Tenant middleware extracting tenant from subdomain, header (`X-Tenant-ID`), or JWT claim
- Tenant-scoped query filters: `.filter(tenant_id=current_tenant)`, `WHERE tenant_id = ?`

### Confidence

- **high** -- row-level security or schema-per-tenant enforced at database level with middleware extracting tenant from auth token
- **medium** -- `tenant_id` column present and filtered in queries but no database-level enforcement
- **low** -- tenant identifier exists in the data model but some queries lack tenant filtering

## Architecture

Look for defense-in-depth tenant boundaries: middleware sets context, queries filter by tenant, database enforces isolation.

### Review Checklist

- Tenant context is set once at the request boundary (middleware/interceptor) and propagated, never parsed repeatedly
- Every data access query includes tenant filtering -- no unscoped queries that could leak cross-tenant data
- Database-level enforcement exists (RLS, schema isolation, or separate databases) as a safety net beyond application code
- Tenant ID is validated against the authenticated user's permissions, not blindly trusted from headers
- Background jobs and async tasks carry tenant context through the execution chain
- Tenant isolation is tested with explicit cross-tenant access attempts

### Anti-patterns

- Relying solely on application-level WHERE clauses with no database enforcement
- Trusting `X-Tenant-ID` header without validating it against the authenticated identity
- Queries that JOIN across tenants or aggregate without tenant scoping
- Missing tenant context in async workers -- background jobs running with no tenant or wrong tenant

### Relationship To Other Concepts

- Related to [tenant-routing](/concepts/tenant-routing) when requests must first reach the correct tenant boundary before isolation can be enforced.
- Related to [multi-tenant](/concepts/multi-tenant) because tenant isolation is one of the main architectural concerns inside multi-tenant systems.
- Related to [rbac](/concepts/rbac) when access rules differ by tenant scope and role membership inside a tenant.

### Boundary

Use `tenant-isolation` when the architecture explicitly prevents one tenant’s data, traffic, or privileges from leaking into another tenant’s boundary.

Do not use it for any tenant-aware code. The key signal is isolation enforcement, not mere tenant tagging.
