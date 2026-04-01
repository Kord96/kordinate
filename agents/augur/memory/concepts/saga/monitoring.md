---
description: Saga — monitoring guidance
---
## Monitoring

Track distributed transaction outcomes and compensation events.

### Key Metrics

- `saga_completed_total` (counter) — successfully finished sagas
- `saga_failed_total` (counter) — sagas that triggered compensation
- `saga_compensation_total` (counter) — individual compensation steps executed
- `saga_duration_seconds` (histogram) — end-to-end saga duration
- `saga_step_duration_seconds` (histogram) — per-step latency to find bottlenecks

### Alerts

- Saga failure rate exceeding threshold
- Compensation failures (compensation step itself failed)
- Saga duration exceeding expected SLA
- Stuck sagas (started but neither completed nor compensated)
