---
description: Blue-Green Deployment — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track health of both environments and switch-over success metrics.

### Key Metrics

- `deployment_active_environment` (gauge) — which environment (blue/green) is currently live
- `deployment_switch_duration_seconds` (histogram) — time to complete traffic cutover
- `deployment_rollback_total` (counter) — rollbacks triggered after switch
- `environment_health_status` (gauge) — readiness of each environment (0=unhealthy, 1=healthy)

### Alerts

- Idle environment health degradation (standby must stay healthy for rollback)
- Error rate spike immediately after traffic switch
- Switch duration exceeding expected window
