---
description: Multi-tenant isolation pattern for shared infrastructure
type: domain-model
abstraction: [architectural, data]
---
# Multi-Tenant

## Recognition

How to identify this pattern in code.

### Signatures

- `tenant_id`, `organization_id`, `org_id` columns present on most or all database tables
- `tenant_context`, `TenantContext`, `current_tenant` middleware or context objects
- `tenant_scope`, `with_tenant` decorators or context managers that filter queries by tenant
- Row-level security policies: `CREATE POLICY ... USING (tenant_id = current_setting('app.tenant_id'))`
- Schema-per-tenant: `CREATE SCHEMA tenant_abc`, `SET search_path TO tenant_abc`
- Python: `django-tenants`, `django-multitenant`, tenant middleware setting `request.tenant`
- JS/TS: `tenant_id` in JWT claims, middleware extracting tenant from subdomain or header
- Go: `tenantID` in context (`context.WithValue`), per-tenant database connection selection
- Rust: `tenant_id` field in request extensions, middleware extracting tenant from auth token
- Java: `@TenantId` annotation, Hibernate multi-tenancy config, `TenantIdentifierResolver`

### Confidence

- **high** -- tenant_id column on all data tables with row-level security or automatic query scoping via middleware, plus per-tenant configuration
- **medium** -- tenant_id in JWT/auth context with manual query filtering in repositories
- **low** -- Organization-level grouping without strict query-level isolation or security policies

## Architecture

### When to use
- SaaS platforms serving multiple customers on shared infrastructure
- Systems where data isolation between organizations is a security and compliance requirement
- Platforms needing per-tenant configuration, feature flags, or usage limits

### Anti-patterns
- Forgetting tenant filters on queries, causing cross-tenant data leakage
- Tenant isolation only at the API layer without database-level enforcement (row-level security)
- Shared caches without tenant-scoped keys, allowing one tenant's data to be served to another

### Complements
- [rbac](/concepts/rbac) — tenant isolation works alongside role-based access within a tenant
- [rate-limiting](/concepts/rate-limiting) — per-tenant rate limits prevent noisy neighbor problems
- [sharding](/concepts/sharding) — large tenants may require dedicated shards for performance isolation

## Impact

Multi-tenancy is a cross-cutting concern that must be enforced at every data access path. A single missing tenant filter is a security vulnerability. Testing must include cross-tenant isolation verification, and monitoring should track per-tenant resource consumption to detect noisy neighbors.
