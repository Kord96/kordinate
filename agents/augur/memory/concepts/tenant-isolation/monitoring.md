---
description: Tenant Isolation — monitoring guidance
---
## Monitoring

Track tenant boundary enforcement, cross-tenant access attempts, and per-tenant resource usage.

### Key Metrics

- `tenant_unscoped_queries_total` (counter) — queries executing without a tenant filter (data leakage risk)
- `tenant_resource_usage` (gauge) — per-tenant query volume, storage, and API call counts for noisy-neighbor detection
- `tenant_rls_policy_status` (gauge) — row-level security enforcement status per table (1=enabled, 0=disabled)
- `tenant_cross_access_blocked_total` (counter) — cross-tenant access attempts caught by the isolation layer
- `tenant_context_propagation_failures_total` (counter) — requests where tenant context was lost in async workers or background jobs
- `tenant_id_validation_failures_total` (counter) — invalid or spoofed tenant ID submissions

### Alerts

- Query executing without a tenant filter detected (immediate cross-tenant leakage risk)
- Row-level security disabled or bypassed on any production table
- Tenant context propagation failure in async worker or background job
- Single tenant consuming disproportionate resources (noisy-neighbor effect)
- Tenant ID validation failure rate elevated (potential spoofing or misconfiguration)
