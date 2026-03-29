---
description: Tenant Isolation — testing guidance
type: supplementary
---
# Testing

- Test cross-tenant access: authenticate as tenant A and attempt to read/write tenant B data (must fail)
- Verify that every data access query includes tenant filtering by inspecting generated SQL in tests
- Test tenant context propagation through async workers and background jobs
- Verify RLS policies by connecting directly to the database and attempting unscoped queries
- Test tenant middleware extraction from subdomain, header, and JWT claim sources
- Test that tenant ID is validated against the authenticated user's permissions, not blindly trusted
- Test tenant onboarding: create a new tenant and verify isolation from day one
- Assert that JOINs and aggregations respect tenant boundaries and do not leak cross-tenant data
