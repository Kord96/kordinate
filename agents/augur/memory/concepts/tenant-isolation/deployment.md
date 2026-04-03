---
description: Tenant Isolation — deployment guidance
type: supplementary
---
## Deployment

Verify that isolation boundaries survive every migration and deployment, since a single missed tenant filter can expose cross-tenant data.

### Rollout Implications

- Database migrations that alter RLS policies or tenant-scoped columns can temporarily disable isolation if the migration runs between the old and new application code
- Schema-per-tenant deployments require migration tooling that applies changes to all tenant schemas atomically — partial application leaves some tenants on the old schema
- Rolling deployments where old and new code coexist may have inconsistent tenant scoping if the new code adds a tenant filter that the old code lacks
- Background job deployments must carry tenant context through the execution chain — deploying new job logic without verifying context propagation can cause jobs to run with no tenant or the wrong tenant
- Changes to auth or routing middleware can silently break tenant ID extraction — a deployment that changes header parsing may route requests to the wrong tenant

### Pre-deploy Checklist

- Verify RLS policies and tenant scoping are active after every database migration before releasing traffic
- Test tenant isolation in staging with explicit cross-tenant access attempts
- Audit tenant ID validation logic in middleware after every deployment touching auth or routing
- Confirm schema-per-tenant migrations have been applied to all tenant schemas, not just the default
- Ensure background jobs carry tenant context end-to-end after deploying changes to job logic
