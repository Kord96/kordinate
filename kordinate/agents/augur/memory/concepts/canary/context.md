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

## Deployment

Route a small percentage of traffic to the new version and promote gradually based on health signals.

### Rollout Implications

- Start with a small traffic slice (1-5%) and increase only after metrics confirm health
- Canary and baseline must run simultaneously — ensure resource capacity for both versions
- Sticky sessions may cause uneven canary exposure; verify traffic distribution is representative

### Pre-deploy Checklist

- Define success criteria (error rate, latency, business metrics) before starting the canary
- Configure automatic rollback triggers tied to the success criteria
- Verify monitoring dashboards compare canary versus baseline side-by-side

