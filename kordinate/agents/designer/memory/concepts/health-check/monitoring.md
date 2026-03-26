---
description: Health Check — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track probe outcomes and dependency health to detect degraded service before users are affected.

### Key Metrics

- `health_check_status` (gauge) — current health state per endpoint (0=down, 1=degraded, 2=up)
- `health_check_duration_seconds` (histogram) — latency of health endpoint responses
- `readiness_probe_failures_total` (counter) — readiness failures triggering traffic removal
- `dependency_health_status` (gauge) — per-dependency connectivity state checked by readiness

### Alerts

- Readiness probe failing for longer than one probe interval (pod removed from service)
- Liveness probe failing (pod restart imminent)
- Health check latency exceeding probe timeout (false failures likely)
- Dependency health degraded across multiple pods simultaneously
