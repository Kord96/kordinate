---
description: Tenant Isolation — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Deployment

- Verify RLS policies and tenant scoping are active after every database migration before releasing traffic
- Deploy schema-per-tenant changes with migration tooling that applies changes to all tenant schemas
- Test tenant isolation in staging with explicit cross-tenant access attempts before production release
- Coordinate tenant onboarding (schema creation, RLS policy, connection pool) as part of deployment
- Roll database-level enforcement changes separately from application changes to isolate failures
- Verify that background job deployments carry tenant context through the execution chain
- Audit tenant ID validation logic in middleware after every deployment touching auth or routing
