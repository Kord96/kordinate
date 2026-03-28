# Testing

- Test cross-tenant access: authenticate as tenant A and attempt to read/write tenant B data (must fail)
- Verify that every data access query includes tenant filtering by inspecting generated SQL in tests
- Test tenant context propagation through async workers and background jobs
- Verify RLS policies by connecting directly to the database and attempting unscoped queries
- Test tenant middleware extraction from subdomain, header, and JWT claim sources
- Test that tenant ID is validated against the authenticated user's permissions, not blindly trusted
- Test tenant onboarding: create a new tenant and verify isolation from day one
- Assert that JOINs and aggregations respect tenant boundaries and do not leak cross-tenant data

# Monitoring

- Alert on queries executing without a tenant filter — unscoped queries risk cross-tenant data leakage
- Track per-tenant resource usage (query volume, storage, API calls) to detect noisy-neighbor effects
- Monitor RLS policy enforcement: alert if row-level security is disabled or bypassed on any table
- Alert on tenant context propagation failures in async workers and background jobs
- Track cross-tenant access attempts that are blocked by the isolation layer
- Dashboard showing per-tenant query rates, latency, and error rates for SLA tracking
- Monitor tenant ID validation failures — elevated rates may indicate spoofing or misconfiguration

# Deployment

- Verify RLS policies and tenant scoping are active after every database migration before releasing traffic
- Deploy schema-per-tenant changes with migration tooling that applies changes to all tenant schemas
- Test tenant isolation in staging with explicit cross-tenant access attempts before production release
- Coordinate tenant onboarding (schema creation, RLS policy, connection pool) as part of deployment
- Roll database-level enforcement changes separately from application changes to isolate failures
- Verify that background job deployments carry tenant context through the execution chain
- Audit tenant ID validation logic in middleware after every deployment touching auth or routing

