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

## Deployment

Maintain two identical environments; deploy to the idle one, verify, then switch traffic atomically.

### Rollout Implications

- Traffic switch is atomic — all users move at once, no gradual rollout
- Database migrations must be backward-compatible since both environments share the data layer
- Keep the old environment running post-switch as an instant rollback target

### Pre-deploy Checklist

- Verify the idle environment mirrors production configuration (env vars, secrets, feature flags)
- Run smoke tests against the idle environment before switching traffic
- Confirm database schema compatibility between both application versions

