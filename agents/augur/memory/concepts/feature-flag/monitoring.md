---
description: Feature Flag/Toggle — monitoring guidance
type: supplementary
---
## Monitoring

Track flag evaluation, stale flags, and variant distribution to maintain control over feature rollouts.

### Key Metrics

- `feature_flag_evaluation_total` (counter) — flag evaluations by flag name and returned variant
- `feature_flag_active_count` (gauge) — number of flags currently in an active (non-fully-rolled-out) state
- `feature_flag_stale_days` (gauge) — days since a flag was last modified, per flag
- `feature_flag_error_total` (counter) — evaluation errors (missing flag, SDK timeout, default fallback used)

### Alerts

- Flag evaluation falling back to default at a high rate (SDK cannot reach the flag service)
- Stale flags older than the configured cleanup threshold (technical debt accumulating)
- Unexpected variant distribution skew for a percentage rollout (targeting rule misconfiguration)
