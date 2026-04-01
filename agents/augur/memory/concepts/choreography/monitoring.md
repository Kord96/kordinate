---
description: Choreography — monitoring guidance
---
## Monitoring

Track event flow across services and dead-letter accumulation to detect broken chains and stalled workflows.

### Key Metrics

- `event_published_total` (counter) — events emitted per service and event type
- `event_consumed_total` (counter) — events processed per consuming service
- `event_processing_duration_seconds` (histogram) — time from event receipt to processing completion
- `dead_letter_events_total` (counter) — events that failed processing and landed in dead-letter
- `event_flow_lag_seconds` (gauge) — end-to-end delay from first event to final outcome per correlation ID

### Alerts

- Published-to-consumed event ratio diverging (events being dropped or not consumed)
- Dead-letter queue depth growing without remediation
- Event processing latency exceeding SLA for any service in the chain
- Correlation IDs with no terminal event within expected time window (stalled workflows)
