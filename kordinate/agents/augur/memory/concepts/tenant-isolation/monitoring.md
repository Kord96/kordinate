---
description: Tenant Isolation — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Monitoring

- Alert on queries executing without a tenant filter — unscoped queries risk cross-tenant data leakage
- Track per-tenant resource usage (query volume, storage, API calls) to detect noisy-neighbor effects
- Monitor RLS policy enforcement: alert if row-level security is disabled or bypassed on any table
- Alert on tenant context propagation failures in async workers and background jobs
- Track cross-tenant access attempts that are blocked by the isolation layer
- Dashboard showing per-tenant query rates, latency, and error rates for SLA tracking
- Monitor tenant ID validation failures — elevated rates may indicate spoofing or misconfiguration
