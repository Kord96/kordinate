---
description: Graceful Degradation — monitoring guidance
type: supplementary
---
## Monitoring

Track degradation activations and dependency health so operators know when the system is running in a reduced mode.

### Key Metrics

- `degradation_active` (gauge) — boolean per feature indicating whether degraded mode is currently active
- `degradation_activations_total` (counter) — number of times degraded mode was triggered, by feature and cause
- `degradation_duration_seconds` (histogram) — how long each degradation episode lasts before recovery
- `dependency_health` (gauge) — health status of each dependency that can trigger degradation (0=down, 1=healthy)

### Alerts

- Degradation active for longer than expected recovery window (dependency not recovering)
- Multiple features degrading simultaneously (systemic issue, not isolated dependency failure)
- Degradation flapping (rapid activation/deactivation suggesting unstable dependency)
