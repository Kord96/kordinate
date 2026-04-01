---
description: Canary Release — monitoring guidance
type: supplementary
---
## Monitoring

Compare canary metrics against the baseline to decide promotion or rollback.

### Key Metrics

- `canary_traffic_ratio` (gauge) — percentage of traffic routed to the canary
- `canary_error_rate` (gauge) — error rate on canary versus baseline
- `canary_latency_seconds` (histogram) — response latency on canary versus baseline
- `canary_promotion_total` (counter) — successful canary promotions to full rollout

### Alerts

- Canary error rate exceeding baseline by configured threshold (auto-rollback trigger)
- Canary latency regression beyond acceptable margin
- Canary stuck at partial traffic (promotion/rollback decision not taken within time window)
